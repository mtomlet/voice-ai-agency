const express = require('express');
const { google } = require('googleapis');
const path = require('path');

const app = express();
app.use(express.json());

// ── Config ──
const SPREADSHEET_ID = '15Ts0s0yImp6Hv_9SuygU4xg-gpJd-Ao1Q2I9fBouuPw';
const SHEET_NAME = 'Sheet1';
const PORT = process.env.PORT || 3000;

// ── Google Sheets Auth ──
const auth = new google.auth.GoogleAuth({
    keyFile: path.join(__dirname, 'credentials.json'),
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
});
const sheets = google.sheets({ version: 'v4', auth });

// ── Helper: Get all rows ──
async function getRows() {
    const res = await sheets.spreadsheets.values.get({
        spreadsheetId: SPREADSHEET_ID,
        range: `${SHEET_NAME}!A:Q`,
    });
    return res.data.values || [];
}

// ── Helper: Normalize phone (strip everything but digits, keep last 10) ──
function normalizePhone(phone) {
    const digits = (phone || '').replace(/\D/g, '');
    return digits.slice(-10);
}

// ════════════════════════════════════════
// WEBHOOK 1: PRE-CALL — Lead Context Lookup
// ════════════════════════════════════════
// Retell sends: { "phone_number": "+16025551234" }
// We return the lead's context so the AI knows who it's calling.

app.post('/pre-call', async (req, res) => {
    try {
        const incomingPhone = normalizePhone(req.body.phone_number || req.body.to_number || '');
        if (!incomingPhone) {
            return res.status(400).json({ error: 'No phone_number provided' });
        }

        const rows = await getRows();
        if (rows.length < 2) {
            return res.status(404).json({ error: 'Sheet is empty' });
        }

        const headers = rows[0];
        const phoneCol = headers.indexOf('phone_number');

        // Find the matching row
        let leadData = null;
        for (let i = 1; i < rows.length; i++) {
            const rowPhone = normalizePhone(rows[i][phoneCol] || '');
            if (rowPhone === incomingPhone) {
                leadData = {};
                headers.forEach((h, idx) => {
                    leadData[h] = rows[i][idx] || '';
                });
                break;
            }
        }

        if (!leadData) {
            return res.status(404).json({ error: 'Lead not found', phone: incomingPhone });
        }

        // Return the context Retell needs for dynamic variables
        console.log(`[PRE-CALL] Found lead: ${leadData.first_name} ${leadData.last_name} (${incomingPhone})`);
        return res.json({
            first_name: leadData.first_name,
            last_name: leadData.last_name,
            phone_number: leadData.phone_number,
            lead_source: leadData.lead_source,
            original_interest: leadData.original_interest,
            agent_name: leadData.agent_name,
            transfer_number: leadData.transfer_number,
        });

    } catch (err) {
        console.error('[PRE-CALL] Error:', err.message);
        return res.status(500).json({ error: 'Internal server error' });
    }
});

// ════════════════════════════════════════
// WEBHOOK 2: POST-CALL — Update Google Sheet
// ════════════════════════════════════════
// Retell sends call results after every call.
// We find the lead's row and update the post-call columns.

app.post('/post-call', async (req, res) => {
    try {
        const data = req.body;
        const incomingPhone = normalizePhone(data.phone_number || '');
        if (!incomingPhone) {
            return res.status(400).json({ error: 'No phone_number provided' });
        }

        const rows = await getRows();
        if (rows.length < 2) {
            return res.status(404).json({ error: 'Sheet is empty' });
        }

        const headers = rows[0];
        const phoneCol = headers.indexOf('phone_number');

        // Find the row index (1-based for Sheets API, +1 for header)
        let rowIndex = -1;
        for (let i = 1; i < rows.length; i++) {
            const rowPhone = normalizePhone(rows[i][phoneCol] || '');
            if (rowPhone === incomingPhone) {
                rowIndex = i + 1; // Sheets is 1-indexed, +1 for header
                break;
            }
        }

        if (rowIndex === -1) {
            return res.status(404).json({ error: 'Lead not found', phone: incomingPhone });
        }

        // Map post-call fields to column letters
        // Columns: A=first_name, B=last_name, C=phone_number, D=lead_source,
        // E=original_interest, F=date_added, G=agent_name, H=transfer_number,
        // I=call_status, J=interest_level, K=timeline, L=pre_approved,
        // M=working_with_agent, N=transfer_attempted, O=notes, P=next_action, Q=last_called
        const today = new Date().toISOString().split('T')[0];
        const updates = [
            data.call_status || '',
            data.interest_level || '',
            data.timeline || '',
            data.pre_approved || '',
            data.working_with_agent || '',
            data.transfer_attempted || '',
            data.notes || '',
            data.next_action || '',
            today,
        ];

        await sheets.spreadsheets.values.update({
            spreadsheetId: SPREADSHEET_ID,
            range: `${SHEET_NAME}!I${rowIndex}:Q${rowIndex}`,
            valueInputOption: 'RAW',
            requestBody: { values: [updates] },
        });

        console.log(`[POST-CALL] Updated lead: ${incomingPhone} → ${data.call_status} / ${data.interest_level}`);
        return res.json({ success: true, row: rowIndex, phone: incomingPhone });

    } catch (err) {
        console.error('[POST-CALL] Error:', err.message);
        return res.status(500).json({ error: 'Internal server error' });
    }
});

// ── Health check ──
app.get('/', (req, res) => {
    res.json({
        status: 'running',
        endpoints: {
            pre_call: 'POST /pre-call — send { phone_number }',
            post_call: 'POST /post-call — send { phone_number, call_status, interest_level, timeline, pre_approved, working_with_agent, transfer_attempted, notes, next_action }',
        }
    });
});

app.listen(PORT, () => {
    console.log(`\n  Lead Reactivation Webhooks running on http://localhost:${PORT}\n`);
    console.log(`  POST /pre-call   → Look up lead context before call`);
    console.log(`  POST /post-call  → Write results back after call\n`);
});
