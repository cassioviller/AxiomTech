import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-primary-dark text-white py-12">
      <div className="container mx-auto px-4 md:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-8 md:mb-0">
            <img 
              src="/images/axiom-logo.png" 
              alt="Axiom Strategic Technologies Logo" 
              className="h-12 mb-4"
              /* Para trocar a logo, substitua o arquivo axiom-logo.png na pasta client/public/images */
            />
            <p className="text-gray-300 text-sm">
              Transformando negócios com engenharia inteligente<br />
              e automação de alto impacto.
            </p>
          </div>
          
          <div className="flex flex-col items-center md:items-end">
            <div className="flex space-x-4 mb-4">
              <a 
                href="https://wa.me/5512982071116" 
                className="bg-white bg-opacity-10 hover:bg-accent rounded-full w-10 h-10 flex items-center justify-center transition-colors duration-200" 
                target="_blank"
                rel="noopener noreferrer"
                aria-label="WhatsApp"
              >
                <i className="fab fa-whatsapp"></i>
              </a>
              <a 
                href="#" 
                className="bg-white bg-opacity-10 hover:bg-accent rounded-full w-10 h-10 flex items-center justify-center transition-colors duration-200" 
                target="_blank"
                rel="noopener noreferrer"
                aria-label="LinkedIn"
              >
                <i className="fab fa-linkedin-in"></i>
              </a>
              <a 
                href="mailto:contato@axiomstrategic.tech" 
                className="bg-white bg-opacity-10 hover:bg-accent rounded-full w-10 h-10 flex items-center justify-center transition-colors duration-200"
                aria-label="Email"
              >
                <i className="fas fa-envelope"></i>
              </a>
            </div>
            <p className="text-gray-300 text-sm text-center md:text-right">
              &copy; {new Date().getFullYear()} Axiom Strategic Technologies.<br />
              Todos os direitos reservados.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
