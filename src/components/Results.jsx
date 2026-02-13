import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';
import { TrendingUp, Clock, DollarSign, Quote } from 'lucide-react';

const Results = () => {
  const containerRef = useRef(null);
  const isInView = useInView(containerRef, { once: true, margin: '-100px' });

  const caseStudies = [
    {
      industry: 'Healthcare Provider',
      title: 'Leading Medical Practice',
      metrics: [
        { label: 'Reduction in Missed Calls', value: '67%', icon: TrendingUp },
        { label: 'Hours Saved Weekly', value: '40+', icon: Clock },
      ],
      quote: "VoiceFlow AI transformed how we handle patient inquiries. Our staff now focuses on care, not phone tags.",
      author: 'Operations Director',
    },
    {
      industry: 'Real Estate Agency',
      title: 'Top-Performing Brokerage',
      metrics: [
        { label: 'Lead Response Time', value: '<30s', icon: Clock },
        { label: 'Increase in Bookings', value: '45%', icon: TrendingUp },
      ],
      quote: "Every lead gets immediate attention now. The AI qualifies them perfectly and books showings while we sleep.",
      author: 'Managing Broker',
    },
    {
      industry: 'Professional Services',
      title: 'Regional Law Firm',
      metrics: [
        { label: 'After-Hours Coverage', value: '100%', icon: Clock },
        { label: 'ROI in First Quarter', value: '340%', icon: DollarSign },
      ],
      quote: "We captured $200K in new business from after-hours calls that would have gone to voicemail.",
      author: 'Senior Partner',
    },
  ];

  return (
    <section className="section-padding bg-noir-800 relative overflow-hidden" ref={containerRef}>
      {/* Large background stat */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={isInView ? { opacity: 0.03 } : {}}
        transition={{ duration: 1 }}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none select-none"
      >
        <span className="font-serif text-[20vw] font-bold text-cream whitespace-nowrap">
          2.4M+
        </span>
      </motion.div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="text-gold/80 text-sm tracking-ultra uppercase">Proven Results</span>
          <h2 className="font-serif text-3xl md:text-5xl font-bold text-cream mt-4 mb-4">
            Success Stories That <span className="text-gradient-gold">Speak Volumes</span>
          </h2>
          <p className="text-cream/60 max-w-2xl mx-auto">
            Real businesses achieving real results with AI-powered voice solutions.
          </p>
        </motion.div>

        {/* Case Studies Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {caseStudies.map((study, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: index * 0.15 }}
              className="glass-card rounded-2xl p-8 border border-gold/10 hover:border-gold/30 transition-all duration-300 group"
            >
              {/* Industry Badge */}
              <div className="mb-6">
                <span className="px-3 py-1 bg-gold/10 rounded-full text-gold text-xs tracking-wide">
                  {study.industry}
                </span>
              </div>

              {/* Title */}
              <h3 className="font-serif text-xl text-cream mb-6">{study.title}</h3>

              {/* Metrics */}
              <div className="space-y-4 mb-8">
                {study.metrics.map((metric, mIndex) => {
                  const Icon = metric.icon;
                  return (
                    <div key={mIndex} className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-lg bg-gold/10 flex items-center justify-center flex-shrink-0">
                        <Icon className="w-5 h-5 text-gold" />
                      </div>
                      <div>
                        <div className="font-serif text-2xl font-bold text-gold">{metric.value}</div>
                        <div className="text-cream/50 text-sm">{metric.label}</div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Quote */}
              <div className="relative">
                <Quote className="absolute -top-2 -left-2 w-8 h-8 text-gold/20" />
                <blockquote className="text-cream/70 text-sm italic leading-relaxed pl-6">
                  "{study.quote}"
                </blockquote>
                <p className="text-cream/40 text-xs mt-3 pl-6">— {study.author}</p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom Stats Bar */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 p-8 glass-card rounded-2xl border border-gold/10"
        >
          <div className="text-center">
            <div className="font-serif text-3xl md:text-4xl font-bold text-gold">500+</div>
            <div className="text-cream/50 text-sm mt-1">Active Deployments</div>
          </div>
          <div className="text-center">
            <div className="font-serif text-3xl md:text-4xl font-bold text-gold">2.4M</div>
            <div className="text-cream/50 text-sm mt-1">Calls Handled</div>
          </div>
          <div className="text-center">
            <div className="font-serif text-3xl md:text-4xl font-bold text-gold">99.7%</div>
            <div className="text-cream/50 text-sm mt-1">Uptime</div>
          </div>
          <div className="text-center">
            <div className="font-serif text-3xl md:text-4xl font-bold text-gold">4.9/5</div>
            <div className="text-cream/50 text-sm mt-1">Client Rating</div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default Results;
