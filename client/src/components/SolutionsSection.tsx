import React from 'react';

const SolutionsSection: React.FC = () => {
  const solutions = [
    {
      title: "Automação Inteligente de Processos",
      description: "Transformamos processos manuais repetitivos em fluxos automatizados inteligentes, incluindo o desenvolvimento de chatbots avançados integrados a CRMs para otimizar a comunicação e a gestão de clientes, reduzindo custos operacionais e aumentando a precisão e eficiência.",
      tags: ["Chatbots Integrados", "Redução de Custos", "Eficiência"],
      image: "/images/solution-automation.jpg" /* Para trocar a imagem, substitua o arquivo solution-automation.jpg na pasta client/public/images */
    },
    {
      title: "Engenharia de Dados e KPIs Estratégicos",
      description: "Desenvolvemos sistemas de coleta, processamento e visualização de dados que transformam informações complexas em insights acionáveis para tomada de decisão.",
      tags: ["Análise de Dados", "Dashboards", "Inteligência de Negócios"],
      image: "/images/solution-data.jpg" /* Para trocar a imagem, substitua o arquivo solution-data.jpg na pasta client/public/images */
    },
    {
      title: "Otimização de Operações e Rotinas Técnicas",
      description: "Redesenhamos seus processos técnicos e operacionais para eliminar gargalos, padronizar procedimentos e maximizar a produtividade da sua equipe.",
      tags: ["Produtividade", "Padronização", "Escalabilidade"],
      image: "/images/solution-operations.jpg" /* Para trocar a imagem, substitua o arquivo solution-operations.jpg na pasta client/public/images */
    }
  ];

  return (
    <section id="solucoes" className="py-20">
      <div className="container mx-auto px-4 md:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto mb-16 text-center reveal">
          <h2 className="section-title">Soluções Estratégicas para Otimizar Sua Performance</h2>
          <div className="w-20 h-1 bg-accent mx-auto mb-8"></div>
          <p className="text-lg text-gray-600">
            Desenvolvemos soluções customizadas que se integram perfeitamente ao seu negócio, potencializando resultados e gerando valor real.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {solutions.map((solution, index) => (
            <div 
              key={index} 
              className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-2 reveal" 
              style={{ animationDelay: `${0.1 * (index + 1)}s` }}
            >
              <div className="h-48 overflow-hidden">
                <img 
                  src={solution.image} 
                  alt={solution.title} 
                  className="w-full h-full object-cover" 
                />
              </div>
              <div className="p-6">
                <h3 className="font-montserrat font-semibold text-xl text-primary-dark mb-4">{solution.title}</h3>
                <p className="text-gray-600 mb-6">{solution.description}</p>
                <div className="flex flex-wrap gap-2">
                  {solution.tags.map((tag, tagIndex) => (
                    <span key={tagIndex} className="text-sm bg-primary-light bg-opacity-30 text-primary-dark px-3 py-1 rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default SolutionsSection;
