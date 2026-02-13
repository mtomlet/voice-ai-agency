import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';
import { PhoneIncoming, PhoneOutgoing, Calendar, UserCheck, Headphones, Sparkles, ArrowRight } from 'lucide-react';

const Services = () => {
  const containerRef = useRef(null);
  const isInView = useInView(containerRef, { once: true, margin: '-100px' });

  const services = [
    {
      icon: PhoneIncoming,
      title: 'Inbound Call Handling',
      description: 'AI agents that answer every call instantly, handle inquiries, and route complex issues to your team.',
      featured: true,
      size: 'large',
    },
    {
      icon: PhoneOutgoing,
      title: 'Outbound Sales Agents',
      description: 'Proactive outreach that qualifies leads and books meetings while you focus on closing.',
      featured: false,
      size: 'medium',
    },
    {
      icon: Calendar,
      title: 'Appointment Scheduling',
      description: 'Seamless calendar integration that books, confirms, and reschedules appointments automatically.',
      featured: false,
      size: 'medium',
    },
    {
      icon: UserCheck,
      title: 'Lead Qualification',
      description: 'Intelligent screening that scores and routes leads based on your criteria.',
      featured: false,
      size: 'small',
    },
    {
      icon: Headphones,
      title: 'Customer Support',
      description: '24/7 support automation that resolves issues and escalates when needed.',
      featured: false,
      size: 'small',
    },
    {
      icon: Sparkles,
      title: 'Custom Solutions',
      description: 'Bespoke voice AI tailored to your industry, workflow, and brand voice.',
      featured: false,
      size: 'small',
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <section id="services" className="section-padding bg-noir-900 relative" ref={containerRef}>
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="text-gold/80 text-sm tracking-ultra uppercase">What We Offer</span>
          <h2 className="font-serif text-3xl md:text-5xl font-bold text-cream mt-4 mb-4">
            Voice AI Solutions Built for <span className="text-gradient-gold">Growth</span>
          </h2>
          <p className="text-cream/60 max-w-2xl mx-auto">
            From inbound support to outbound sales, our AI voice agents handle
            the conversations that matter most to your business.
          </p>
        </motion.div>

        {/* Bento Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate={isInView ? 'visible' : 'hidden'}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {services.map((service, index) => {
            const Icon = service.icon;
            const isLarge = service.size === 'large';

            return (
              <motion.div
                key={index}
                variants={itemVariants}
                className={`group relative glass-card rounded-2xl p-8 cursor-pointer
                  transition-all duration-500 hover:border-gold/30
                  ${isLarge ? 'md:col-span-2 lg:col-span-1 lg:row-span-2' : ''}
                  ${service.featured ? 'border-gold/20' : 'border-white/5'}
                `}
              >
                {/* Gold shimmer border on hover */}
                <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none">
                  <div className="absolute inset-0 rounded-2xl gold-border-shimmer" />
                </div>

                <div className="relative z-10">
                  {/* Icon */}
                  <div className={`
                    w-14 h-14 rounded-xl bg-gradient-to-br from-gold/20 to-gold/5
                    flex items-center justify-center mb-6
                    group-hover:from-gold/30 group-hover:to-gold/10 transition-all duration-300
                  `}>
                    <Icon className="w-7 h-7 text-gold" />
                  </div>

                  {/* Content */}
                  <h3 className={`font-serif text-xl md:text-2xl text-cream mb-3 ${isLarge ? 'text-2xl md:text-3xl' : ''}`}>
                    {service.title}
                  </h3>
                  <p className={`text-cream/60 leading-relaxed mb-6 ${isLarge ? 'text-base' : 'text-sm'}`}>
                    {service.description}
                  </p>

                  {/* Learn More Link */}
                  <div className="flex items-center gap-2 text-gold text-sm font-medium group/link">
                    <span className="animated-underline">Learn More</span>
                    <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover/link:translate-x-1" />
                  </div>
                </div>

                {/* Featured badge */}
                {service.featured && (
                  <div className="absolute top-4 right-4 px-3 py-1 bg-gold/20 rounded-full">
                    <span className="text-gold text-xs tracking-wide">Popular</span>
                  </div>
                )}
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
};

export default Services;
