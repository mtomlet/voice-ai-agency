#!/bin/bash
# Deploy Calendar Integration Modal Functions
# Run this from the airbnb-mansion-in-the-sky/ directory
#
# Prerequisites:
# 1. Modal CLI installed: pip install modal
# 2. Modal token set: modal token set --token-id $MODAL_TOKEN_ID --token-secret $MODAL_TOKEN_SECRET
# 3. Google Calendar shared with service account:
#    mark-496@automation-reminder-481818.iam.gserviceaccount.com
#    (Share techtomlet@gmail.com calendar with "Make changes to events" permission)

set -e

echo "========================================="
echo "Deploying Airbnb Calendar Functions"
echo "========================================="

# Set Modal tokens from .env.calendar if available
if [ -f .env.calendar ]; then
    export MODAL_TOKEN_ID=$(grep MODAL_TOKEN_ID .env.calendar | cut -d= -f2)
    export MODAL_TOKEN_SECRET=$(grep MODAL_TOKEN_SECRET .env.calendar | cut -d= -f2)
fi

echo ""
echo "Step 1: Deploying check-availability..."
echo "-----------------------------------------"
CHECK_OUTPUT=$(modal deploy check-availability.py 2>&1)
echo "$CHECK_OUTPUT"
CHECK_URL=$(echo "$CHECK_OUTPUT" | grep -oP 'https://[^ ]+\.modal\.run' | head -1)
echo "CHECK URL: $CHECK_URL"

echo ""
echo "Step 2: Deploying book-appointment..."
echo "-----------------------------------------"
BOOK_OUTPUT=$(modal deploy book-appointment.py 2>&1)
echo "$BOOK_OUTPUT"
BOOK_URL=$(echo "$BOOK_OUTPUT" | grep -oP 'https://[^ ]+\.modal\.run' | head -1)
echo "BOOK URL: $BOOK_URL"

echo ""
echo "========================================="
echo "DEPLOYMENT COMPLETE"
echo "========================================="
echo "Check Availability URL: ${CHECK_URL}/check-availability"
echo "Book Appointment URL:   ${BOOK_URL}/book-appointment"
echo "========================================="

# Save URLs to .env.calendar
if [ -n "$CHECK_URL" ] && [ -n "$BOOK_URL" ]; then
    # Remove old URLs if present
    sed -i '/CHECK_AVAILABILITY_URL=/d' .env.calendar 2>/dev/null || true
    sed -i '/BOOK_APPOINTMENT_URL=/d' .env.calendar 2>/dev/null || true
    # Add new URLs
    echo "CHECK_AVAILABILITY_URL=${CHECK_URL}/check-availability" >> .env.calendar
    echo "BOOK_APPOINTMENT_URL=${BOOK_URL}/book-appointment" >> .env.calendar
    echo ""
    echo "URLs saved to .env.calendar"
fi

echo ""
echo "Step 3: Testing endpoints..."
echo "-----------------------------------------"
if [ -n "$CHECK_URL" ]; then
    echo "Testing check-availability..."
    curl -s -X POST "${CHECK_URL}/check-availability" \
        -H "Content-Type: application/json" \
        -d '{"check_in":"2026-03-15","check_out":"2026-03-22"}' | python3 -m json.tool
fi

if [ -n "$BOOK_URL" ]; then
    echo ""
    echo "Testing book-appointment..."
    curl -s -X POST "${BOOK_URL}/book-appointment" \
        -H "Content-Type: application/json" \
        -d '{"check_in":"2026-04-01","check_out":"2026-04-05","guest_name":"Test User","guest_email":"test@test.com","guest_phone":"555-0000","group_size":2}' | python3 -m json.tool
fi

echo ""
echo "Done! Update Retell agent tools with these URLs."
