import React, { useEffect } from 'react';
import Navbar from '@/components/Navbar';
import HeroSection from '@/components/HeroSection';
import AboutSection from '@/components/AboutSection';
import SolutionsSection from '@/components/SolutionsSection';
import MethodologySection from '@/components/MethodologySection';
import ResultsSection from '@/components/ResultsSection';
import ContactSection from '@/components/ContactSection';
import Footer from '@/components/Footer';

const HomePage: React.FC = () => {
  useEffect(() => {
    // Back to top button functionality
    const toggleBackToTopButton = () => {
      const backToTopButton = document.getElementById('back-to-top');
      if (!backToTopButton) return;
      
      if (window.pageYOffset > 300) {
        backToTopButton.classList.remove('opacity-0', 'invisible');
        backToTopButton.classList.add('opacity-100', 'visible');
      } else {
        backToTopButton.classList.remove('opacity-100', 'visible');
        backToTopButton.classList.add('opacity-0', 'invisible');
      }
    };
    
    // Initial check
    toggleBackToTopButton();
    
    // Add scroll event listener
    window.addEventListener('scroll', toggleBackToTopButton);
    
    // Cleanup
    return () => {
      window.removeEventListener('scroll', toggleBackToTopButton);
    };
  }, []);
  
  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  };
  
  return (
    <>
      <Navbar />
      <HeroSection />
      <AboutSection />
      <SolutionsSection />
      <MethodologySection />
      <ResultsSection />
      <ContactSection />
      <Footer />
      
      {/* Back to top button */}
      <button 
        id="back-to-top" 
        onClick={scrollToTop}
        className="fixed bottom-6 right-6 bg-accent text-white w-12 h-12 rounded-full flex items-center justify-center shadow-lg opacity-0 invisible transition-all duration-300 z-50"
        aria-label="Voltar ao topo"
      >
        <i className="fas fa-arrow-up"></i>
      </button>
    </>
  );
};

export default HomePage;
