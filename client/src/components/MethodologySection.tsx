import React from 'react';

const MethodologySection: React.FC = () => {
  const methodologySteps = [
    {
      number: "1",
      title: "Diagnóstico",
      description: "Entendemos profundamente seus desafios, processos e objetivos de negócio através de uma análise detalhada e mapeamento de fluxos atuais.",
      checkpoints: [
        "Mapeamento de processos atuais",
        "Identificação de pontos de melhoria",
        "Definição de métricas de sucesso"
      ]
    },
    {
      number: "2",
      title: "Desenho da Solução",
      description: "Desenhamos arquiteturas de solução customizadas que atendem às suas necessidades específicas, considerando tecnologia, pessoas e processos.",
      checkpoints: [
        "Arquitetura de solução customizada",
        "Seleção de tecnologias adequadas",
        "Planejamento de implementação"
      ]
    },
    {
      number: "3",
      title: "Desenvolvimento Ágil",
      description: "Utilizamos metodologias ágeis para desenvolver e testar sua solução de forma iterativa, permitindo ajustes e validações contínuas.",
      checkpoints: [
        "Implementação por sprints",
        "Validações contínuas com stakeholders",
        "Adaptação baseada em feedback"
      ]
    },
    {
      number: "4",
      title: "Implementação",
      description: "Realizamos a implementação completa com treinamento de usuários, documentação e transição suave para a nova solução.",
      checkpoints: [
        "Implementação completa em produção",
        "Treinamento de usuários",
        "Documentação técnica e de usuário"
      ]
    },
    {
      number: "5",
      title: "Acompanhamento",
      description: "Monitoramos os resultados, fornecemos suporte contínuo e identificamos oportunidades de melhorias e expansões futuras.",
      checkpoints: [
        "Monitoramento de métricas de sucesso",
        "Suporte técnico e de usuários",
        "Identificação de oportunidades de expansão"
      ]
    }
  ];

  return (
    <section id="abordagem" className="py-20 custom-gradient">
      <div className="container mx-auto px-4 md:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto mb-16 text-center reveal">
          <h2 className="font-montserrat font-bold text-3xl md:text-4xl text-white mb-4">
            Nossa Metodologia: Da Análise à Implementação de Alto Impacto
          </h2>
          <div className="w-20 h-1 bg-accent mx-auto mb-8"></div>
          <p className="text-lg text-gray-100">
            Um processo estruturado e comprovado para entregar soluções que geram resultados reais e mensuráveis.
          </p>
        </div>
        
        <div className="relative">
          {/* Desktop timeline line */}
          <div className="hidden md:block absolute left-1/2 top-0 bottom-0 w-1 bg-accent transform -translate-x-1/2 z-0"></div>
          
          {methodologySteps.map((step, index) => (
            <div 
              key={index} 
              className={`md:flex items-center justify-between mb-16 md:mb-24 reveal ${index === methodologySteps.length - 1 ? 'mb-0' : ''}`}
            >
              <div className={`md:w-5/12 mb-8 md:mb-0 md:pr-12 text-right ${index % 2 !== 0 ? 'order-1 md:order-2' : ''}`}>
                <h3 className="font-montserrat font-semibold text-2xl text-white mb-4">
                  {step.number}. {step.title}
                </h3>
                <p className="text-gray-100">{step.description}</p>
              </div>
              
              {/* Timeline circle */}
              <div className="hidden md:block absolute left-1/2 transform -translate-x-1/2 z-20">
                <div className="bg-accent text-white w-12 h-12 rounded-full flex items-center justify-center font-montserrat font-bold text-xl shadow-lg">
                  {step.number}
                </div>
              </div>
              
              <div className={`md:w-5/12 md:pl-12 ${index % 2 !== 0 ? 'order-2 md:order-1' : ''}`}>
                <div className="bg-white bg-opacity-10 p-6 rounded-xl border border-white border-opacity-20">
                  <ul className="text-gray-100 space-y-2">
                    {step.checkpoints.map((checkpoint, cpIndex) => (
                      <li key={cpIndex} className="flex items-start">
                        <i className="fas fa-check-circle text-accent mt-1 mr-2"></i>
                        <span>{checkpoint}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default MethodologySection;
