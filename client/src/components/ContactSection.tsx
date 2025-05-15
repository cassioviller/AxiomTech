import React, { useState, FormEvent } from 'react';
import { useToast } from '@/hooks/use-toast';

interface FormData {
  name: string;
  company: string;
  email: string;
  message: string;
}

const ContactSection: React.FC = () => {
  const { toast } = useToast();
  const [formData, setFormData] = useState<FormData>({
    name: '',
    company: '',
    email: '',
    message: ''
  });
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    // Validate form
    if (!formData.name || !formData.email || !formData.message) {
      toast({
        title: "Erro no formulário",
        description: "Por favor, preencha todos os campos obrigatórios.",
        variant: "destructive"
      });
      return;
    }
    
    // Send form data (in a real implementation, this would be sent to a server)
    toast({
      title: "Mensagem enviada",
      description: "Obrigado por entrar em contato! Em breve retornaremos.",
    });
    
    // Reset form
    setFormData({
      name: '',
      company: '',
      email: '',
      message: ''
    });
  };

  return (
    <section id="contato" className="py-20 bg-white">
      <div className="container mx-auto px-4 md:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto mb-16 text-center reveal">
          <h2 className="section-title">Inicie a Transformação da Sua Empresa Hoje</h2>
          <div className="w-20 h-1 bg-accent mx-auto mb-8"></div>
          <p className="text-lg text-gray-600">
            Entre em contato com Cássio Viller e a Axiom Strategic Technologies para discutir seus desafios.
          </p>
        </div>
        
        <div className="flex flex-col md:flex-row gap-8 lg:gap-16">
          <div className="md:w-5/12 reveal">
            <div className="custom-gradient rounded-xl p-8 text-white h-full">
              <h3 className="font-montserrat font-semibold text-2xl mb-6">Fale Conosco</h3>
              
              <div className="space-y-6">
                <div className="flex items-start">
                  <div className="bg-white bg-opacity-20 rounded-full p-3 mr-4">
                    <i className="fas fa-phone text-white"></i>
                  </div>
                  <div>
                    <h4 className="font-montserrat font-semibold text-white mb-1">WhatsApp</h4>
                    <a href="https://wa.me/5512982071116" className="text-gray-100 hover:text-accent transition-colors duration-200" target="_blank" rel="noopener noreferrer">
                      +55 12 98207-1116
                    </a>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="bg-white bg-opacity-20 rounded-full p-3 mr-4">
                    <i className="fas fa-envelope text-white"></i>
                  </div>
                  <div>
                    <h4 className="font-montserrat font-semibold text-white mb-1">E-mail</h4>
                    <a href="mailto:contato@axiomstrategic.tech" className="text-gray-100 hover:text-accent transition-colors duration-200">
                      contato@axiomstrategic.tech
                    </a>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="bg-white bg-opacity-20 rounded-full p-3 mr-4">
                    <i className="fab fa-linkedin text-white"></i>
                  </div>
                  <div>
                    <h4 className="font-montserrat font-semibold text-white mb-1">LinkedIn</h4>
                    <a href="#" className="text-gray-100 hover:text-accent transition-colors duration-200" target="_blank" rel="noopener noreferrer">
                      Cássio Viller
                    </a>
                  </div>
                </div>
              </div>
              
              <div className="mt-12">
                <a 
                  href="https://wa.me/5512982071116" 
                  className="inline-flex items-center justify-center w-full bg-accent hover:bg-opacity-90 text-white font-montserrat font-semibold px-6 py-4 rounded-full shadow-lg transition-all duration-300 transform hover:-translate-y-1" 
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <i className="fab fa-whatsapp text-2xl mr-2"></i>
                  Contate via WhatsApp
                </a>
              </div>
            </div>
          </div>
          
          <div className="md:w-7/12 reveal" style={{ animationDelay: '0.2s' }}>
            <form className="bg-gray-100 rounded-xl p-8" onSubmit={handleSubmit}>
              <h3 className="font-montserrat font-semibold text-2xl text-primary-dark mb-6">Envie sua Mensagem</h3>
              
              <div className="space-y-6">
                <div>
                  <label htmlFor="name" className="block text-gray-700 font-medium mb-2">Nome</label>
                  <input 
                    type="text" 
                    id="name" 
                    name="name" 
                    value={formData.name}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-primary focus:ring-2 focus:ring-primary focus:ring-opacity-50 outline-none transition-colors duration-200" 
                    placeholder="Seu nome completo"
                    required
                  />
                </div>
                
                <div>
                  <label htmlFor="company" className="block text-gray-700 font-medium mb-2">Empresa</label>
                  <input 
                    type="text" 
                    id="company" 
                    name="company" 
                    value={formData.company}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-primary focus:ring-2 focus:ring-primary focus:ring-opacity-50 outline-none transition-colors duration-200" 
                    placeholder="Nome da sua empresa"
                  />
                </div>
                
                <div>
                  <label htmlFor="email" className="block text-gray-700 font-medium mb-2">E-mail</label>
                  <input 
                    type="email" 
                    id="email" 
                    name="email" 
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-primary focus:ring-2 focus:ring-primary focus:ring-opacity-50 outline-none transition-colors duration-200" 
                    placeholder="seu.email@empresa.com"
                    required
                  />
                </div>
                
                <div>
                  <label htmlFor="message" className="block text-gray-700 font-medium mb-2">Mensagem</label>
                  <textarea 
                    id="message" 
                    name="message" 
                    rows={4} 
                    value={formData.message}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-primary focus:ring-2 focus:ring-primary focus:ring-opacity-50 outline-none transition-colors duration-200 resize-none" 
                    placeholder="Descreva seu desafio ou projeto..."
                    required
                  ></textarea>
                </div>
                
                <button 
                  type="submit" 
                  className="w-full bg-primary hover:bg-primary-dark text-white font-montserrat font-semibold px-6 py-4 rounded-lg shadow-lg transition-all duration-300 transform hover:-translate-y-1"
                >
                  Enviar Mensagem
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ContactSection;
