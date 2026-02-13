import { motion } from 'framer-motion';
import { ArrowRight, Play } from 'lucide-react';

const Hero = () => {
  const scrollToSection = (href) => {
    const element = document.querySelector(href);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden noise-overlay">
      {/* Animated Background Shapes */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Floating geometric shapes */}
        <motion.div
          animate={{
            y: [0, -30, 0],
            rotate: [0, 5, 0],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="absolute top-1/4 left-1/4 w-64 h-64 border border-gold/10 rotate-45"
        />
        <motion.div
          animate={{
            y: [0, 20, 0],
            rotate: [0, -5, 0],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="absolute bottom-1/4 right-1/4 w-96 h-96 border border-gold/5 rounded-full"
        />
        <motion.div
          animate={{
            y: [0, -20, 0],
            x: [0, 10, 0],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="absolute top-1/3 right-1/3 w-32 h-32 bg-gold/5 rotate-12"
        />

        {/* Gradient overlays */}
        <div className="absolute inset-0 bg-gradient-to-b from-noir-900 via-transparent to-noir-900" />
        <div className="absolute inset-0 bg-gradient-to-r from-noir-900/50 via-transparent to-noir-900/50" />
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 md:px-12 text-center">
        {/* Pre-headline badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 px-4 py-2 border border-gold/30 rounded-full mb-8"
        >
          <span className="w-2 h-2 bg-gold rounded-full animate-pulse" />
          <span className="text-gold/80 text-sm tracking-wide">Premium Voice AI Solutions</span>
        </motion.div>

        {/* Main Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="font-serif text-4xl md:text-6xl lg:text-7xl font-bold text-cream leading-tight mb-6"
        >
          AI Voice Agents That{' '}
          <span className="text-gradient-gold">Sound Human</span>
          <br />
          <span className="text-cream/90">Convert Like Champions</span>
        </motion.h1>

        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-cream/60 text-lg md:text-xl max-w-2xl mx-auto mb-12 leading-relaxed"
        >
          Transform missed calls into closed deals. Our AI agents handle inbound calls,
          qualify leads, and book appointments 24/7—with the warmth and intelligence
          your customers deserve.
        </motion.p>

        {/* CTAs */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16"
        >
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => scrollToSection('#cta')}
            className="btn-primary flex items-center gap-3"
          >
            Schedule Discovery Call
            <ArrowRight size={18} />
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => scrollToSection('#demo')}
            className="btn-secondary flex items-center gap-3"
          >
            <Play size={18} />
            See It In Action
          </motion.button>
        </motion.div>

        {/* Trust Indicators */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="flex flex-wrap items-center justify-center gap-8 md:gap-12"
        >
          <div className="text-center">
            <div className="font-serif text-3xl md:text-4xl font-bold text-gold">500+</div>
            <div className="text-cream/50 text-sm tracking-wide">Businesses Served</div>
          </div>
          <div className="w-px h-12 bg-white/10 hidden md:block" />
          <div className="text-center">
            <div className="font-serif text-3xl md:text-4xl font-bold text-gold">2.4M</div>
            <div className="text-cream/50 text-sm tracking-wide">Calls Handled</div>
          </div>
          <div className="w-px h-12 bg-white/10 hidden md:block" />
          <div className="text-center">
            <div className="font-serif text-3xl md:text-4xl font-bold text-gold">99.7%</div>
            <div className="text-cream/50 text-sm tracking-wide">Uptime Reliability</div>
          </div>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="w-6 h-10 border border-gold/30 rounded-full flex items-start justify-center p-2"
        >
          <motion.div
            animate={{ y: [0, 12, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-1 h-2 bg-gold rounded-full"
          />
        </motion.div>
      </motion.div>
    </section>
  );
};

export default Hero;
