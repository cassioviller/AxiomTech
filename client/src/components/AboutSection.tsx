import React from 'react';

const AboutSection: React.FC = () => {
  return (
    <section id="sobre" className="py-20 bg-gray-100">
      <div className="container mx-auto px-4 md:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto mb-16 text-center reveal">
          <h2 className="section-title">Sobre a Axiom: A Interseção da Engenharia com a Inovação Tecnológica</h2>
          <div className="w-20 h-1 bg-accent mx-auto mb-8"></div>
        </div>
        
        <div className="flex flex-col md:flex-row gap-12 items-center">
          <div className="w-full md:w-5/12 lg:w-4/12 reveal">
            <div className="relative overflow-hidden rounded-xl custom-shadow bg-white p-2">
              {/* Profile picture placeholder */}
              <div className="bg-primary bg-opacity-10 rounded-lg overflow-hidden">
                {/* Using a professional business photo from stock images */}
                <img 
                  src="https://images.unsplash.com/photo-1560250097-0b93528c311a?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=600&h=800" 
                  alt="Cássio Viller - CEO da Axiom Strategic Technologies" 
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="bg-primary-dark text-white text-center py-3 rounded-b-lg mt-1">
                <h3 className="font-montserrat font-semibold">Cássio Viller</h3>
                <p className="text-sm text-primary-light">Fundador & CEO</p>
              </div>
            </div>
          </div>
          
          <div className="w-full md:w-7/12 lg:w-8/12 reveal" style={{ animationDelay: '0.2s' }}>
            <p className="text-lg text-gray-dark mb-8">
              A Axiom Strategic Technologies nasceu da visão de Cássio Viller em unir sua expertise única em Engenharia Civil e Sistemas de Informação para criar soluções que verdadeiramente transformam operações corporativas. Nossa missão é proporcionar automação inteligente e otimização de processos que não apenas modernizem operações, mas gerem retorno sobre investimento mensurável e significativo.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
              {[
                {
                  icon: "fa-sync-alt",
                  title: "Visão Integrada",
                  description: "Engenharia Civil + Sistemas de Informação para uma abordagem verdadeiramente holística às necessidades do seu negócio."
                },
                {
                  icon: "fa-chart-line",
                  title: "Foco em ROI",
                  description: "Automação Inteligente com retorno sobre investimento comprovado e mensurável desde o primeiro mês."
                },
                {
                  icon: "fa-tachometer-alt",
                  title: "Abordagem Ágil",
                  description: "Metodologias ágeis e prototipagem rápida para implementações eficientes e adaptáveis às suas necessidades."
                },
                {
                  icon: "fa-handshake",
                  title: "Parceria Estratégica",
                  description: "Compromisso com resultados a longo prazo através de soluções customizadas e acompanhamento contínuo."
                }
              ].map((card, index) => (
                <div key={index} className="bg-white rounded-xl p-6 custom-shadow hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                  <div className="flex items-start mb-4">
                    <div className="bg-primary-light rounded-full p-3 mr-4">
                      <i className={`fas ${card.icon} text-primary-dark text-xl`}></i>
                    </div>
                    <h3 className="font-montserrat font-semibold text-lg text-primary-dark">{card.title}</h3>
                  </div>
                  <p className="text-gray-600">{card.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AboutSection;
