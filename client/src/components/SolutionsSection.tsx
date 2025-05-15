import React from 'react';

const SolutionsSection: React.FC = () => {
  const solutions = [
    {
      title: "Automação Inteligente de Processos",
      description: "Transformamos processos manuais repetitivos em fluxos automatizados inteligentes, reduzindo custos operacionais e aumentando a precisão e eficiência.",
      tags: ["Redução de Custos", "Eficiência", "Precisão"],
      image: "https://images.unsplash.com/photo-1563986768494-4dee2763ff3f?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=800&h=500"
    },
    {
      title: "Engenharia de Dados e KPIs Estratégicos",
      description: "Desenvolvemos sistemas de coleta, processamento e visualização de dados que transformam informações complexas em insights acionáveis para tomada de decisão.",
      tags: ["Análise de Dados", "Dashboards", "Inteligência de Negócios"],
      image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=800&h=500"
    },
    {
      title: "Otimização de Operações e Rotinas Técnicas",
      description: "Redesenhamos seus processos técnicos e operacionais para eliminar gargalos, padronizar procedimentos e maximizar a produtividade da sua equipe.",
      tags: ["Produtividade", "Padronização", "Escalabilidade"],
      image: "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=800&h=500"
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
