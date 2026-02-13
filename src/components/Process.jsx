import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';
import { MessageSquare, Lightbulb, Code2, TestTube, Rocket } from 'lucide-react';

const Process = () => {
  const containerRef = useRef(null);
  const isInView = useInView(containerRef, { once: true, margin: '-100px' });

  const steps = [
    {
      number: '01',
      icon: MessageSquare,
      title: 'Discovery Call',
      description: 'We dive deep into your business, understand your call flows, and identify opportunities for AI-powered automation.',
    },
    {
      number: '02',
      icon: Lightbulb,
      title: 'Strategy & Design',
      description: 'Our team crafts a custom voice AI solution tailored to your brand voice, workflows, and integration requirements.',
    },
    {
      number: '03',
      icon: Code2,
      title: 'Build & Train',
      description: 'We develop your AI agent, train it on your knowledge base, and fine-tune responses for natural conversations.',
    },
    {
      number: '04',
      icon: TestTube,
      title: 'Testing & Refinement',
      description: 'Rigorous testing with real scenarios ensures your agent handles edge cases gracefully and sounds authentic.',
    },
    {
      number: '05',
      icon: Rocket,
      title: 'Launch & Optimize',
      description: 'Go live with full support. We continuously monitor performance and optimize based on real call data.',
    },
  ];

  return (
    <section id="process" className="section-padding bg-noir-900 relative overflow-hidden" ref={containerRef}>
      {/* Background decorations */}
      <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-gold/5 to-transparent" />

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <span className="text-gold/80 text-sm tracking-ultra uppercase">Our Process</span>
          <h2 className="font-serif text-3xl md:text-5xl font-bold text-cream mt-4 mb-4">
            From Concept to <span className="text-gradient-gold">Conversation</span>
          </h2>
          <p className="text-cream/60 max-w-2xl mx-auto">
            A proven methodology for deploying voice AI that delivers results from day one.
          </p>
        </motion.div>

        {/* Timeline */}
        <div className="relative">
          {/* Connecting line */}
          <div className="hidden lg:block absolute left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-gold/0 via-gold/30 to-gold/0" />

          {/* Steps */}
          <div className="space-y-12 lg:space-y-24">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isEven = index % 2 === 0;

              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: isEven ? -50 : 50 }}
                  animate={isInView ? { opacity: 1, x: 0 } : {}}
                  transition={{ duration: 0.6, delay: index * 0.15 }}
                  className={`relative flex flex-col lg:flex-row items-center gap-8 ${
                    isEven ? 'lg:flex-row' : 'lg:flex-row-reverse'
                  }`}
                >
                  {/* Content */}
                  <div className={`flex-1 ${isEven ? 'lg:text-right' : 'lg:text-left'}`}>
                    <div className={`inline-block ${isEven ? 'lg:ml-auto' : ''}`}>
                      <div className="glass-card rounded-2xl p-8 max-w-md border border-gold/10 hover:border-gold/30 transition-colors duration-300">
                        <span className="text-gold font-serif text-4xl font-bold opacity-30">
                          {step.number}
                        </span>
                        <h3 className="font-serif text-2xl text-cream mt-2 mb-3">
                          {step.title}
                        </h3>
                        <p className="text-cream/60 leading-relaxed">
                          {step.description}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Center icon */}
                  <div className="relative z-10 flex-shrink-0">
                    <motion.div
                      whileHover={{ scale: 1.1 }}
                      className="w-16 h-16 rounded-full bg-gradient-to-br from-gold to-gold-dark
                               flex items-center justify-center shadow-lg shadow-gold/20"
                    >
                      <Icon className="w-7 h-7 text-noir-900" />
                    </motion.div>
                    {/* Pulse ring */}
                    <motion.div
                      initial={{ scale: 1, opacity: 0.5 }}
                      animate={{ scale: 1.5, opacity: 0 }}
                      transition={{ duration: 2, repeat: Infinity }}
                      className="absolute inset-0 rounded-full border-2 border-gold"
                    />
                  </div>

                  {/* Spacer for layout */}
                  <div className="flex-1 hidden lg:block" />
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="text-center mt-20"
        >
          <p className="text-cream/60 mb-6">Ready to transform your phone system?</p>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => document.querySelector('#cta')?.scrollIntoView({ behavior: 'smooth' })}
            className="btn-primary"
          >
            Start Your Journey
          </motion.button>
        </motion.div>
      </div>
    </section>
  );
};

export default Process;
