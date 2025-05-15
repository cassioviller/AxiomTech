import React from 'react';

const ContactSection: React.FC = () => {

  return (
    <section id="contato" className="py-20 bg-white">
      <div className="container mx-auto px-4 md:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto mb-16 text-center reveal">
          <h2 className="section-title">Fale Diretamente Conosco via WhatsApp</h2>
          <div className="w-20 h-1 bg-accent mx-auto mb-8"></div>
          <p className="text-lg text-gray-600">
            Entre em contato com Cássio Viller e a Axiom Strategic Technologies para discutir seus desafios e transformar sua empresa hoje mesmo.
          </p>
        </div>
        
        <div className="max-w-3xl mx-auto">
          <div className="custom-gradient rounded-xl p-12 text-white reveal">
            <div className="text-center mb-10">
              <div className="bg-white bg-opacity-10 rounded-full p-5 inline-block mb-6">
                <i className="fab fa-whatsapp text-white text-4xl"></i>
              </div>
              <h3 className="font-montserrat font-semibold text-3xl mb-4">Contato Rápido e Eficiente</h3>
              <p className="text-gray-100 text-lg mb-8">
                Converse diretamente com nossa equipe para uma resposta rápida às suas necessidades de automação e transformação digital.
              </p>
            </div>
            
            <div className="flex justify-center">
              <a 
                href="https://wa.me/5512982071116" 
                className="inline-flex items-center justify-center bg-accent hover:bg-opacity-90 text-white font-montserrat font-semibold px-10 py-5 rounded-full shadow-lg transition-all duration-300 transform hover:-translate-y-1 text-xl" 
                target="_blank"
                rel="noopener noreferrer"
              >
                <i className="fab fa-whatsapp text-3xl mr-3"></i>
                Iniciar Conversa no WhatsApp
              </a>
            </div>
            
            <div className="text-center mt-10 text-gray-100 text-sm opacity-80">
              Estamos disponíveis em horário comercial para atendê-lo da melhor forma.
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ContactSection;
