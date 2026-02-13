import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';
import { Check, Sparkles } from 'lucide-react';

const Pricing = () => {
  const containerRef = useRef(null);
  const isInView = useInView(containerRef, { once: true, margin: '-100px' });

  const plans = [
    {
      name: 'Starter',
      price: '$2,500',
      period: '/month',
      description: 'Perfect for small businesses ready to automate their first line of communication.',
      features: [
        'Single AI voice agent',
        'Up to 500 calls/month',
        'Business hours coverage',
        'Basic lead capture',
        'Email notifications',
        'Standard integrations',
        'Email support',
      ],
      cta: 'Get Started',
      highlighted: false,
    },
    {
      name: 'Growth',
      price: '$5,500',
      period: '/month',
      description: 'For growing businesses that need comprehensive coverage and advanced features.',
      features: [
        'Up to 3 AI voice agents',
        'Up to 2,000 calls/month',
        '24/7 availability',
        'Advanced lead qualification',
        'CRM integration',
        'Custom voice & personality',
        'Appointment scheduling',
        'Analytics dashboard',
        'Priority support',
      ],
      cta: 'Get Started',
      highlighted: true,
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: '',
      description: 'Tailored solutions for organizations with complex needs and high volumes.',
      features: [
        'Unlimited AI agents',
        'Unlimited call volume',
        'Multi-location support',
        'Custom integrations',
        'Dedicated account manager',
        'White-label options',
        'SLA guarantees',
        'On-premise deployment',
        'Custom training & compliance',
      ],
      cta: 'Contact Us',
      highlighted: false,
    },
  ];

  return (
    <section id="pricing" className="section-padding bg-noir-900 relative" ref={containerRef}>
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <span className="text-gold/80 text-sm tracking-ultra uppercase">Investment</span>
          <h2 className="font-serif text-3xl md:text-5xl font-bold text-cream mt-4 mb-4">
            Simple, Transparent <span className="text-gradient-gold">Pricing</span>
          </h2>
          <p className="text-cream/60 max-w-2xl mx-auto">
            Choose the plan that fits your business. All plans include setup, training, and ongoing optimization.
          </p>
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: index * 0.15 }}
              className={`relative rounded-2xl p-8 ${
                plan.highlighted
                  ? 'bg-gradient-to-b from-gold/20 to-gold/5 border-2 border-gold'
                  : 'glass-card border border-white/5'
              }`}
            >
              {/* Popular badge */}
              {plan.highlighted && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <div className="flex items-center gap-2 px-4 py-2 bg-gold rounded-full">
                    <Sparkles className="w-4 h-4 text-noir-900" />
                    <span className="text-noir-900 text-xs font-bold tracking-wide uppercase">Most Popular</span>
                  </div>
                </div>
              )}

              {/* Plan Header */}
              <div className="mb-8">
                <h3 className="font-serif text-2xl text-cream mb-2">{plan.name}</h3>
                <div className="flex items-baseline gap-1 mb-4">
                  <span className="font-serif text-4xl md:text-5xl font-bold text-gold">{plan.price}</span>
                  <span className="text-cream/50">{plan.period}</span>
                </div>
                <p className="text-cream/60 text-sm">{plan.description}</p>
              </div>

              {/* Features List */}
              <ul className="space-y-4 mb-8">
                {plan.features.map((feature, fIndex) => (
                  <li key={fIndex} className="flex items-start gap-3">
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${
                      plan.highlighted ? 'bg-gold' : 'bg-gold/20'
                    }`}>
                      <Check className={`w-3 h-3 ${plan.highlighted ? 'text-noir-900' : 'text-gold'}`} />
                    </div>
                    <span className="text-cream/70 text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              {/* CTA Button */}
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => document.querySelector('#cta')?.scrollIntoView({ behavior: 'smooth' })}
                className={`w-full py-4 rounded-lg font-semibold tracking-wide text-sm transition-all duration-300 ${
                  plan.highlighted
                    ? 'bg-gold text-noir-900 hover:bg-gold-light'
                    : 'border border-gold text-gold hover:bg-gold hover:text-noir-900'
                }`}
              >
                {plan.cta}
              </motion.button>
            </motion.div>
          ))}
        </div>

        {/* Bottom Note */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="text-center mt-12"
        >
          <p className="text-cream/40 text-sm">
            All plans include a 30-day money-back guarantee. Need a custom solution?{' '}
            <button
              onClick={() => document.querySelector('#cta')?.scrollIntoView({ behavior: 'smooth' })}
              className="text-gold hover:underline"
            >
              Let's talk
            </button>
          </p>
        </motion.div>
      </div>
    </section>
  );
};

export default Pricing;
