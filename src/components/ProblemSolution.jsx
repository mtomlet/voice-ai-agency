import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef, useState, useEffect } from 'react';
import { XCircle, CheckCircle, PhoneOff, Clock, DollarSign, Users, Phone, Calendar, Target, Headphones } from 'lucide-react';

const AnimatedCounter = ({ end, suffix = '', duration = 2 }) => {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  useEffect(() => {
    if (isInView) {
      let startTime;
      const animate = (currentTime) => {
        if (!startTime) startTime = currentTime;
        const progress = Math.min((currentTime - startTime) / (duration * 1000), 1);
        setCount(Math.floor(progress * end));
        if (progress < 1) {
          requestAnimationFrame(animate);
        }
      };
      requestAnimationFrame(animate);
    }
  }, [isInView, end, duration]);

  return <span ref={ref}>{count}{suffix}</span>;
};

const ProblemSolution = () => {
  const containerRef = useRef(null);
  const isInView = useInView(containerRef, { once: true, margin: '-100px' });

  const problems = [
    { icon: PhoneOff, text: 'Missing calls means missing revenue' },
    { icon: Clock, text: 'Staff overwhelmed with repetitive inquiries' },
    { icon: DollarSign, text: 'High cost of 24/7 call center coverage' },
    { icon: Users, text: 'Inconsistent customer experience across shifts' },
  ];

  const solutions = [
    { icon: Phone, text: 'Every call answered instantly, 24/7/365' },
    { icon: Calendar, text: 'Automated appointment booking & lead capture' },
    { icon: Target, text: 'Intelligent lead qualification on every call' },
    { icon: Headphones, text: 'Consistent, premium experience every time' },
  ];

  const stats = [
    { value: 67, suffix: '%', label: 'Reduction in Missed Calls' },
    { value: 45, suffix: '%', label: 'Increase in Bookings' },
    { value: 12000, suffix: '+', label: 'Hours Saved Annually' },
  ];

  return (
    <section className="section-padding bg-noir-800 relative overflow-hidden" ref={containerRef}>
      {/* Background accent */}
      <div className="absolute top-0 left-0 w-1/2 h-full bg-gradient-to-r from-red-950/10 to-transparent" />
      <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-gold/5 to-transparent" />

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="text-gold/80 text-sm tracking-ultra uppercase">The Challenge</span>
          <h2 className="font-serif text-3xl md:text-5xl font-bold text-cream mt-4">
            Stop Losing Customers to <span className="text-gradient-gold">Voicemail</span>
          </h2>
        </motion.div>

        {/* Problem / Solution Split */}
        <div className="grid md:grid-cols-2 gap-8 md:gap-16 mb-20">
          {/* Problems */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <div className="glass-card rounded-2xl p-8 border-red-900/20">
              <h3 className="font-serif text-2xl text-cream mb-6 flex items-center gap-3">
                <span className="w-8 h-8 rounded-full bg-red-900/30 flex items-center justify-center">
                  <XCircle className="w-5 h-5 text-red-400" />
                </span>
                The Problem
              </h3>
              <div className="space-y-4">
                {problems.map((item, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={isInView ? { opacity: 1, x: 0 } : {}}
                    transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                    className="flex items-center gap-4 p-4 bg-noir-700/50 rounded-lg border border-red-900/10"
                  >
                    <item.icon className="w-5 h-5 text-red-400/70 flex-shrink-0" />
                    <span className="text-cream/70">{item.text}</span>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Solutions */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <div className="glass-card rounded-2xl p-8 border-gold/10">
              <h3 className="font-serif text-2xl text-cream mb-6 flex items-center gap-3">
                <span className="w-8 h-8 rounded-full bg-gold/20 flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-gold" />
                </span>
                The Solution
              </h3>
              <div className="space-y-4">
                {solutions.map((item, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: 20 }}
                    animate={isInView ? { opacity: 1, x: 0 } : {}}
                    transition={{ duration: 0.4, delay: 0.5 + index * 0.1 }}
                    className="flex items-center gap-4 p-4 bg-noir-700/50 rounded-lg border border-gold/10"
                  >
                    <item.icon className="w-5 h-5 text-gold flex-shrink-0" />
                    <span className="text-cream/80">{item.text}</span>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8"
        >
          {stats.map((stat, index) => (
            <div
              key={index}
              className="text-center p-8 glass-card rounded-xl border border-gold/10"
            >
              <div className="font-serif text-4xl md:text-5xl font-bold text-gold mb-2">
                <AnimatedCounter end={stat.value} suffix={stat.suffix} />
              </div>
              <div className="text-cream/60 text-sm tracking-wide">{stat.label}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default ProblemSolution;
