import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';
import { ArrowRight, Shield, Clock, Headphones } from 'lucide-react';

const CTA = () => {
  const containerRef = useRef(null);
  const isInView = useInView(containerRef, { once: true, margin: '-100px' });

  const badges = [
    { icon: Shield, text: '30-Day Guarantee' },
    { icon: Clock, text: 'Setup in 2 Weeks' },
    { icon: Headphones, text: '24/7 Support' },
  ];

  return (
    <section id="cta" className="section-padding bg-noir-900 relative overflow-hidden" ref={containerRef}>
      {/* Background effects */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-gold/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-gold/5 rounded-full blur-3xl" />
      </div>

      <div className="max-w-4xl mx-auto relative z-10 text-center">
        {/* Main content */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
        >
          <span className="text-gold/80 text-sm tracking-ultra uppercase">Ready to Transform?</span>

          <h2 className="font-serif text-3xl md:text-5xl lg:text-6xl font-bold text-cream mt-6 mb-6 leading-tight">
            Stop Losing Revenue to <br />
            <span className="text-gradient-gold">Voicemail</span>
          </h2>

          <p className="text-cream/60 text-lg md:text-xl max-w-2xl mx-auto mb-12 leading-relaxed">
            Every missed call is a missed opportunity. Let our AI handle the conversations
            while you focus on growing your business. Schedule a free discovery call today.
          </p>

          {/* CTA Button */}
          <motion.a
            href="https://calendly.com/mark-oceansideaisolutions/ai-voice-pioneers-onboarding"
            target="_blank"
            rel="noopener noreferrer"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="inline-flex items-center gap-3 btn-primary text-base px-10 py-5"
          >
            Schedule Your Discovery Call
            <ArrowRight className="w-5 h-5" />
          </motion.a>

          {/* Trust badges */}
          <div className="flex flex-wrap items-center justify-center gap-8 mt-12">
            {badges.map((badge, index) => {
              const Icon = badge.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={isInView ? { opacity: 1, y: 0 } : {}}
                  transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                  className="flex items-center gap-2"
                >
                  <Icon className="w-5 h-5 text-gold/70" />
                  <span className="text-cream/50 text-sm">{badge.text}</span>
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        {/* Contact info */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-16 pt-12 border-t border-white/5"
        >
          <p className="text-cream/40 text-sm mb-4">Prefer to reach out directly?</p>
          <div className="flex flex-wrap items-center justify-center gap-8">
            <a
              href="mailto:hello@voiceflowai.com"
              className="text-cream/60 hover:text-gold transition-colors"
            >
              hello@voiceflowai.com
            </a>
            <span className="text-cream/20 hidden md:block">|</span>
            <a
              href="tel:+18005551234"
              className="text-cream/60 hover:text-gold transition-colors"
            >
              (800) 555-1234
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default CTA;
