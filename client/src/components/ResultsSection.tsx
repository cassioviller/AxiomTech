import React from 'react';

const ResultsSection: React.FC = () => {
  const results = [
    {
      value: "258%",
      label: "ROI no primeiro mês"
    },
    {
      value: "120+",
      label: "Horas mensais economizadas"
    },
    {
      value: "97%",
      label: "Redução de erros operacionais"
    }
  ];

  return (
    <section id="resultados" className="py-20 bg-gray-100">
      <div className="container mx-auto px-4 md:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto mb-16 text-center reveal">
          <h2 className="section-title">Resultados que Impulsionam o Sucesso</h2>
          <div className="w-20 h-1 bg-accent mx-auto mb-8"></div>
          <p className="text-lg text-gray-600">
            Conheça como nossas soluções transformam operações e geram valor mensurável para nossos clientes.
          </p>
        </div>
        
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden reveal">
          <div className="md:flex">
            <div className="md:w-5/12">
              <img 
                src="https://images.unsplash.com/photo-1507679799987-c73779587ccf?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=800&h=1000" 
                alt="Case de Sucesso: Automação de Processos Corporativos" 
                className="w-full h-full object-cover" 
              />
            </div>
            
            <div className="md:w-7/12 p-8 md:p-12">
              <div className="flex items-center mb-6">
                <div className="bg-primary-light rounded-full p-2 mr-4">
                  <i className="fas fa-trophy text-primary-dark"></i>
                </div>
                <h3 className="font-montserrat font-semibold text-2xl text-primary-dark">
                  Case Principal: Automação de Processos Corporativos
                </h3>
              </div>
              
              <div className="mb-8">
                <h4 className="font-montserrat font-semibold text-lg text-primary mb-2">O Desafio</h4>
                <p className="text-gray-600">
                  Uma grande corporação enfrentava desafios significativos com processos manuais repetitivos que consumiam mais de 120 horas mensais de trabalho da equipe técnica, gerando atrasos, inconsistências e custos elevados.
                </p>
              </div>
              
              <div className="mb-8">
                <h4 className="font-montserrat font-semibold text-lg text-primary mb-2">Nossa Solução</h4>
                <p className="text-gray-600">
                  Implementamos uma solução de automação inteligente que integrou sistemas legados, criou fluxos de trabalho automatizados e dashboards em tempo real para monitoramento de KPIs críticos.
                </p>
              </div>
              
              <div className="mb-8">
                <h4 className="font-montserrat font-semibold text-lg text-primary mb-2">Resultados Quantitativos</h4>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">
                  {results.map((result, index) => (
                    <div key={index} className="bg-gray-100 rounded-xl p-4 text-center">
                      <span className="text-accent font-montserrat font-bold text-4xl">{result.value}</span>
                      <p className="text-gray-600 text-sm mt-2">{result.label}</p>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="italic text-gray-600 text-sm border-l-4 border-primary-light pl-4">
                Este é um exemplo do impacto que podemos gerar para sua empresa através de soluções customizadas de engenharia inteligente e automação.
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ResultsSection;
