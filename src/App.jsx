import Navigation from './components/Navigation';
import Hero from './components/Hero';
import ProblemSolution from './components/ProblemSolution';
import Services from './components/Services';
import VoiceDemo from './components/VoiceDemo';
import Process from './components/Process';
import Results from './components/Results';
import Pricing from './components/Pricing';
import FAQ from './components/FAQ';
import CTA from './components/CTA';
import Footer from './components/Footer';

function App() {
  return (
    <div className="min-h-screen bg-noir-900">
      <Navigation />
      <main>
        <Hero />
        <ProblemSolution />
        <Services />
        <VoiceDemo />
        <Process />
        <Results />
        <Pricing />
        <FAQ />
        <CTA />
      </main>
      <Footer />
    </div>
  );
}

export default App;
