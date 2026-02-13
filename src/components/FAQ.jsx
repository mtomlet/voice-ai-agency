import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';
import { ChevronDown } from 'lucide-react';

const FAQ = () => {
  const containerRef = useRef(null);
  const isInView = useInView(containerRef, { once: true, margin: '-100px' });
  const [openIndex, setOpenIndex] = useState(null);

  const faqs = [
    {
      question: 'How long does it take to get set up?',
      answer: 'Most deployments go live within 2-3 weeks. This includes discovery, custom training, integration setup, and testing. Complex enterprise deployments may take 4-6 weeks. We\'ll provide a detailed timeline during your discovery call.',
    },
    {
      question: 'Will the AI sound robotic?',
      answer: 'Not at all. Our AI agents use advanced natural language processing and voice synthesis to create conversations that feel genuinely human. We customize the voice, personality, and speech patterns to match your brand. Try our live demo above to hear for yourself.',
    },
    {
      question: 'What systems can you integrate with?',
      answer: 'We integrate with all major CRMs (Salesforce, HubSpot, Zoho), calendar systems (Google Calendar, Calendly, Acuity), phone systems (RingCentral, Twilio, Vonage), and custom APIs. If you use it, we can likely connect to it.',
    },
    {
      question: 'How do you handle complex or unusual requests?',
      answer: 'Our AI is trained to recognize its limitations. When a call falls outside its capabilities, it gracefully transfers to a human team member, schedules a callback, or takes a detailed message. You maintain full control over escalation rules.',
    },
    {
      question: 'Is my data secure?',
      answer: 'Absolutely. We\'re SOC 2 Type II compliant and HIPAA-ready for healthcare clients. All calls are encrypted in transit and at rest. We never share your data or use it to train models for other clients. You own your data completely.',
    },
    {
      question: 'What happens if the AI makes a mistake?',
      answer: 'We continuously monitor call quality and have built-in safeguards. Every call is logged for review. If issues arise, our team addresses them immediately and retrains the model. Most clients see continuous improvement over the first 30 days.',
    },
    {
      question: 'Can I customize what the AI says?',
      answer: 'Yes, completely. During onboarding, we work with you to define scripts, responses, and conversation flows. You can update these anytime through our dashboard. The AI learns your terminology, products, and preferred communication style.',
    },
    {
      question: 'What\'s your uptime guarantee?',
      answer: 'We maintain 99.7% uptime across our platform. Enterprise clients receive SLA-backed guarantees with financial penalties for any downtime. Our infrastructure is distributed across multiple cloud providers for maximum reliability.',
    },
  ];

  return (
    <section id="faq" className="section-padding bg-noir-800 relative" ref={containerRef}>
      <div className="max-w-3xl mx-auto">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="text-gold/80 text-sm tracking-ultra uppercase">FAQ</span>
          <h2 className="font-serif text-3xl md:text-5xl font-bold text-cream mt-4 mb-4">
            Common <span className="text-gradient-gold">Questions</span>
          </h2>
          <p className="text-cream/60">
            Everything you need to know about getting started with voice AI.
          </p>
        </motion.div>

        {/* Accordion */}
        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.4, delay: index * 0.05 }}
              className={`glass-card rounded-xl overflow-hidden border transition-colors duration-300 ${
                openIndex === index ? 'border-gold/30' : 'border-white/5'
              }`}
            >
              <button
                onClick={() => setOpenIndex(openIndex === index ? null : index)}
                className="w-full flex items-center justify-between p-6 text-left"
              >
                <span className={`font-medium transition-colors duration-300 ${
                  openIndex === index ? 'text-gold' : 'text-cream'
                }`}>
                  {faq.question}
                </span>
                <motion.div
                  animate={{ rotate: openIndex === index ? 180 : 0 }}
                  transition={{ duration: 0.3 }}
                  className={`flex-shrink-0 ml-4 ${
                    openIndex === index ? 'text-gold' : 'text-cream/50'
                  }`}
                >
                  <ChevronDown className="w-5 h-5" />
                </motion.div>
              </button>

              <AnimatePresence>
                {openIndex === index && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="px-6 pb-6">
                      <p className="text-cream/60 leading-relaxed">{faq.answer}</p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>

        {/* Still have questions */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="text-center mt-12"
        >
          <p className="text-cream/60 mb-4">Still have questions?</p>
          <button
            onClick={() => document.querySelector('#cta')?.scrollIntoView({ behavior: 'smooth' })}
            className="text-gold hover:underline font-medium"
          >
            Schedule a call with our team →
          </button>
        </motion.div>
      </div>
    </section>
  );
};

export default FAQ;
