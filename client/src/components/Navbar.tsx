import React, { useState, useEffect } from 'react';
import { scrollToElement } from '@/lib/utils';
import axiomLogo from '@assets/a-logo-design-showcasing-the-text-axiom-_3_1LiL1rT564AFHLfP5wlA_nsXscy4YRDO5r3k1oDu0Pg.png';

const Navbar: React.FC = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 100) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };
    
    window.addEventListener('scroll', handleScroll);
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);
  
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };
  
  const handleNavLinkClick = (sectionId: string) => {
    scrollToElement(sectionId);
    setIsMobileMenuOpen(false);
  };
  
  return (
    <header className={`fixed top-0 left-0 right-0 z-50 bg-white shadow-md transition-all duration-300 ${isScrolled ? 'py-2' : 'py-3'}`}>
      <div className="container mx-auto px-4 md:px-6 lg:px-8">
        <div className="flex justify-between items-center">
          <a 
            href="#hero" 
            className="flex items-center"
            onClick={(e) => {
              e.preventDefault();
              handleNavLinkClick('hero');
            }}
          >
            <img 
              src={axiomLogo} 
              alt="Axiom Strategic Technologies Logo" 
              className="h-14"
            />
          </a>
          
          {/* Mobile menu button */}
          <button 
            type="button" 
            className="lg:hidden text-primary-dark focus:outline-none" 
            onClick={toggleMobileMenu}
            aria-label={isMobileMenuOpen ? "Fechar menu" : "Abrir menu"}
            aria-expanded={isMobileMenuOpen}
          >
            <i className={`fas ${isMobileMenuOpen ? 'fa-times' : 'fa-bars'} text-2xl`}></i>
          </button>
          
          {/* Desktop navigation */}
          <nav className="hidden lg:flex items-center space-x-8">
            {[
              { id: 'sobre', label: 'Sobre' },
              { id: 'solucoes', label: 'Soluções' },
              { id: 'abordagem', label: 'Abordagem' },
              { id: 'resultados', label: 'Resultados' }
            ].map((item) => (
              <a 
                key={item.id}
                href={`#${item.id}`}
                className="text-primary hover:text-accent font-medium transition-colors duration-200"
                onClick={(e) => {
                  e.preventDefault();
                  handleNavLinkClick(item.id);
                }}
              >
                {item.label}
              </a>
            ))}
            <a 
              href="#contato"
              className="font-montserrat bg-accent hover:bg-opacity-90 text-white font-semibold px-6 py-2 rounded-full shadow-sm transition-all duration-200"
              onClick={(e) => {
                e.preventDefault();
                handleNavLinkClick('contato');
              }}
            >
              Contato
            </a>
          </nav>
        </div>
      </div>
      
      {/* Mobile navigation menu */}
      <nav className={`lg:hidden ${isMobileMenuOpen ? 'block' : 'hidden'} bg-white border-t border-gray-200 absolute w-full left-0 shadow-md transition-all duration-300`}>
        <div className="container mx-auto px-4 py-3 flex flex-col space-y-4">
          {[
            { id: 'sobre', label: 'Sobre' },
            { id: 'solucoes', label: 'Soluções' },
            { id: 'abordagem', label: 'Abordagem' },
            { id: 'resultados', label: 'Resultados' },
            { id: 'contato', label: 'Contato' }
          ].map((item) => (
            <a 
              key={item.id}
              href={`#${item.id}`}
              className="py-2 px-4 text-primary hover:text-accent font-medium border-l-4 border-transparent hover:border-accent transition-colors duration-200"
              onClick={(e) => {
                e.preventDefault();
                handleNavLinkClick(item.id);
              }}
            >
              {item.label}
            </a>
          ))}
        </div>
      </nav>
    </header>
  );
};

export default Navbar;
