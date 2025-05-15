import React from 'react';
import { scrollToElement } from '@/lib/utils';

const HeroSection: React.FC = () => {
  return (
    <section id="hero" className="pt-24 min-h-screen flex items-center relative">
      {/* Background image with overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat z-0" 
        style={{ 
          backgroundImage: 'url("https://images.unsplash.com/photo-1557683316-973673baf926?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1920&h=1080")',
          /* URL_DA_IMAGEM_DE_FUNDO_AQUI - replace with your preferred image */
        }}
      ></div>
      
      {/* Dark gradient overlay for readability */}
      <div className="absolute inset-0 bg-gradient-to-r from-primary-dark via-primary to-primary-dark opacity-90 z-10"></div>
      
      {/* Pattern overlay for added texture */}
      <div className="absolute inset-0 pattern-overlay z-20 opacity-10"></div>

      <div className="container mx-auto px-4 md:px-6 lg:px-8 py-16 md:py-20 lg:py-24 relative z-30">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="font-montserrat font-bold text-3xl md:text-4xl lg:text-5xl text-white leading-tight mb-6 text-shadow reveal">
            Axiom Strategic Technologies: Engenharia Inteligente e Automação de Alto Impacto para Transformar Seu Negócio.
          </h1>
          <p className="text-lg md:text-xl text-gray-100 mb-10 max-w-3xl mx-auto reveal" style={{ animationDelay: '0.2s' }}>
            Capacitando grandes organizações a alcançar excelência operacional e ROI significativo através de soluções customizadas lideradas por Cássio Viller.
          </p>
          <button
            onClick={() => scrollToElement('solucoes')}
            className="inline-block font-montserrat bg-accent hover:bg-opacity-90 text-white font-semibold text-lg px-8 py-4 rounded-full shadow-lg transition-all duration-300 transform hover:-translate-y-1 reveal"
            style={{ animationDelay: '0.4s' }}
          >
            Descubra Nossas Soluções
          </button>
        </div>
      </div>
      
      <div className="absolute bottom-0 left-0 right-0 z-30">
        <div className="w-full custom-gradient h-24 opacity-60" style={{ clipPath: 'polygon(0 100%, 100% 100%, 100% 0, 0 100%)' }}></div>
      </div>
    </section>
  );
};

export default HeroSection;
