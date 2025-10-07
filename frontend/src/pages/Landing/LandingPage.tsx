import { useState } from "react";
import {
  TrendingUp,
  PieChart,
  Shield,
  Zap,
  CheckCircle,
  Users,
  Calendar,
  Globe,
  Menu,
  X,
  ArrowRight,
  Star,
} from "lucide-react";

// Simulamos la importación de componentes
import { ReactNode, MouseEventHandler } from "react";

type ButtonProps = {
  variant?: "primary" | "secondary" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  children?: ReactNode;
  className?: string;
  onClick?: MouseEventHandler<HTMLButtonElement>;
  [key: string]: any;
};

const Button = ({
  variant = "primary",
  size = "md",
  loading = false,
  children,
  className = "",
  onClick,
  ...props
}: ButtonProps) => {
  const baseClasses =
    "inline-flex items-center justify-center gap-2 font-medium transition-all duration-200 ease-in-out focus:outline-none disabled:cursor-not-allowed";

  const sizeClasses = {
    sm: "px-3 py-1.5 text-sm rounded-md",
    md: "px-4 py-2 text-sm rounded-lg",
    lg: "px-6 py-3 text-base rounded-lg",
  };

  const variantClasses = {
    primary:
      "bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 disabled:bg-gray-300",
    secondary:
      "bg-green-600 text-white hover:bg-green-700 active:bg-green-800 disabled:bg-green-300",
    outline:
      "border border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white",
    ghost: "text-gray-600 hover:bg-gray-100",
  };

  return (
    <button
      className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`}
      onClick={onClick}
      disabled={loading}
      {...props}
    >
      {loading && (
        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
      )}
      {children}
    </button>
  );
};

type CardProps = {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
};

const Card = ({ children, className = "", hover = true }: CardProps) => (
  <div
    className={`bg-white border border-gray-200 rounded-xl shadow-sm ${
      hover
        ? "hover:shadow-md hover:-translate-y-1 transition-all duration-200"
        : ""
    } ${className}`}
  >
    {children}
  </div>
);

type FeatureCardProps = {
  icon: React.ReactNode;
  title: string;
  description: string;
};

const FeatureCard = ({ icon, title, description }: FeatureCardProps) => (
  <Card className="p-6 text-center">
    <div className="flex justify-center mb-4">
      <div className="w-12 h-12 flex items-center justify-center rounded-lg bg-blue-600 text-white">
        {icon}
      </div>
    </div>
    <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
    <p className="text-gray-600 leading-relaxed">{description}</p>
  </Card>
);

const TestimonialCard = ({
  content = "",
  author = "",
  role = "",
  rating = 5,
}) => (
  <Card className="p-6">
    <div className="flex mb-4">
      {Array.from({ length: 5 }).map((_, i) => (
        <Star
          key={i}
          className={`w-5 h-5 ${
            i < rating ? "text-yellow-400 fill-current" : "text-gray-300"
          }`}
        />
      ))}
    </div>
    <blockquote className="text-gray-600 mb-4 leading-relaxed">
      "{content}"
    </blockquote>
    <div className="flex items-center">
      <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center mr-3">
        <span className="text-white font-medium">{author.charAt(0)}</span>
      </div>
      <div>
        <div className="font-medium text-gray-900">{author}</div>
        <div className="text-sm text-gray-500">{role}</div>
      </div>
    </div>
  </Card>
);

const BenefitCard = ({ icon, title, description }: FeatureCardProps) => (
  <div className="flex items-start">
    <div className="flex-shrink-0 mr-4">
      <div className="w-8 h-8 flex items-center justify-center rounded-full bg-green-100 text-green-600">
        {icon}
      </div>
    </div>
    <div>
      <h4 className="font-medium text-gray-900 mb-2">{title}</h4>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  </div>
);

// Hook simulado para demo
const useDemo = () => {
  const [isCreating, setIsCreating] = useState(false);

  const createDemoUser = async () => {
    setIsCreating(true);
    // Simular llamada a la API
    await new Promise((resolve) => setTimeout(resolve, 2000));
    alert("¡Demo creado exitosamente! Redirigiendo al dashboard...");
    setIsCreating(false);
  };

  return { isCreating, createDemoUser };
};

export default function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { isCreating, createDemoUser } = useDemo();

  const features = [
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Reportes en tiempo real",
      description:
        "Accede a informes detallados de tus ingresos y gastos con actualización automática de datos.",
    },
    {
      icon: <PieChart className="w-6 h-6" />,
      title: "Análisis inteligente de gastos",
      description:
        "Usa Chart.js y reportes automáticos para entender tus hábitos financieros.",
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Privacidad y seguridad",
      description: "Tus datos están protegidos con autenticación JWT estricta.",
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Alertas inteligentes",
      description:
        "Recibe una app que notificaciones personalizadas sobre tus límites de gasto.",
    },
  ];

  const benefits = [
    {
      icon: <CheckCircle className="w-5 h-5" />,
      title: "100% Free",
      description: "Acceso completo a todas las funciones sin costo.",
    },
    {
      icon: <Users className="w-5 h-5" />,
      title: "Real Connections",
      description:
        "Conecta con una comunidad de usuarios que comparten tus objetivos.",
    },
    {
      icon: <Calendar className="w-5 h-5" />,
      title: "Flexible Schedules",
      description: "Adapta la app a tu ritmo de vida y preferencias.",
    },
    {
      icon: <Globe className="w-5 h-5" />,
      title: "Global Community",
      description:
        "Únete a miles de usuarios que ya transformaron sus finanzas.",
    },
  ];

  const testimonials = [
    {
      content:
        "FinTrack has revolutionized my personal finance management. It's not just a financial management app, but an insightful tool that helps me make informed decisions.",
      author: "Jessica",
      role: "Diseñadora UX",
      rating: 5,
    },
    {
      content:
        "Love FinTrack's flexibility. I can use it for my financial history, trends, and receive notifications of type warnings when I exceed my budget.",
      author: "Robert",
      role: "Freelancer",
      rating: 5,
    },
    {
      content:
        "The platform is well laid out and shows comprehensive data FinTrack offers incredible support. It allows me to buy those financial habits at a glance.",
      author: "Maria",
      role: "Estudiante",
      rating: 5,
    },
  ];

  const handleDemoClick = async () => {
    await createDemoUser();
  };

  const handleLoginClick = () => {
    alert("Redirigiendo a la página de login...");
  };

  const handleRegisterClick = () => {
    alert("Redirigiendo a la página de registro...");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* HEADER */}
      <header className="bg-slate-100 border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <TrendingUp className="w-8 h-8 text-blue-600 mr-2" />
              <span className="text-xl font-bold text-gray-900">FinTrack</span>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-8">
              <a
                href="#inicio"
                className="text-gray-700 hover:text-blue-600 transition-colors"
              >
                Inicio
              </a>
              <a
                href="#transacciones"
                className="text-gray-700 hover:text-blue-600 transition-colors"
              >
                Transacciones
              </a>
              <a
                href="#reportes"
                className="text-gray-700 hover:text-blue-600 transition-colors"
              >
                Reportes
              </a>
              <a
                href="#metas"
                className="text-gray-700 hover:text-blue-600 transition-colors"
              >
                Metas
              </a>
            </nav>

            {/* Desktop Buttons */}
            <div className="hidden md:flex items-center space-x-3">
              <Button
                variant="secondary"
                onClick={handleDemoClick}
                loading={isCreating}
              >
                Probar demo
              </Button>
              <Button variant="primary" onClick={handleLoginClick}>
                Iniciar sesión
              </Button>
            </div>

            {/* Mobile Menu Button */}
            <button
              className="md:hidden p-2 text-gray-700"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-gray-200">
              <nav className="flex flex-col space-y-2">
                <a
                  href="#inicio"
                  className="py-2 text-gray-700 hover:text-blue-600"
                >
                  Inicio
                </a>
                <a
                  href="#transacciones"
                  className="py-2 text-gray-700 hover:text-blue-600"
                >
                  Transacciones
                </a>
                <a
                  href="#reportes"
                  className="py-2 text-gray-700 hover:text-blue-600"
                >
                  Reportes
                </a>
                <a
                  href="#metas"
                  className="py-2 text-gray-700 hover:text-blue-600"
                >
                  Metas
                </a>
                <div className="flex flex-col space-y-2 pt-2">
                  <Button
                    variant="secondary"
                    onClick={handleDemoClick}
                    loading={isCreating}
                  >
                    Probar demo
                  </Button>
                  <Button variant="primary" onClick={handleLoginClick}>
                    Iniciar sesión
                  </Button>
                </div>
              </nav>
            </div>
          )}
        </div>
      </header>

      {/* HERO SECTION */}
      <section className="py-20 bg-gradient-to-br from-blue-50 to-green-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Hero Content */}
            <div>
              <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 mb-6">
                Toma el control de
                <span className="text-transparent bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text">
                  {" "}
                  tus finanzas personales
                </span>
              </h1>
              <p className="text-xl text-gray-600 mb-8 leading-relaxed">
                Visualiza, analiza y mejora tus hábitos financieros desde una
                plataforma intuitiva y completa.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button
                  variant="secondary"
                  size="lg"
                  onClick={handleDemoClick}
                  loading={isCreating}
                  className="flex items-center"
                >
                  <Zap className="w-5 h-5 mr-2" />
                  Probar demo sin registrarse
                </Button>
                <Button
                  variant="primary"
                  size="lg"
                  onClick={handleRegisterClick}
                  className="flex items-center"
                >
                  Crear Cuenta
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </div>
            </div>

            {/* Hero Image */}
            <div className="relative">
              <div className="bg-white rounded-2xl shadow-2xl p-8 transform rotate-3 hover:rotate-0 transition-transform duration-300">
                <div className="aspect-video bg-gradient-to-br from-blue-100 to-green-100 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <TrendingUp className="w-16 h-16 text-blue-600 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-800">
                      Interface intuitiva
                    </h3>
                    <p className="text-sm text-gray-600 mt-2">
                      Dashboard completo
                    </p>
                  </div>
                </div>
              </div>
              <div className="absolute -bottom-4 -left-4 bg-green-600 text-white px-4 py-2 rounded-full shadow-lg">
                <span className="text-sm font-medium">100% Gratuito</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES SECTION */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Características principales
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Descubre cómo FinTrack puede transformar tu manera de gestionar el
              dinero.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <FeatureCard
                key={index}
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
              />
            ))}
          </div>
        </div>
      </section>

      {/* GALLERY SECTION */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Galería visual
            </h2>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Screenshot 1 */}
            <Card className="overflow-hidden">
              <div className="aspect-video bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                <div className="text-center text-white">
                  <PieChart className="w-12 h-12 mx-auto mb-2" />
                  <p className="font-medium">Interfaz clara e intuitiva</p>
                </div>
              </div>
            </Card>

            {/* Screenshot 2 */}
            <Card className="overflow-hidden">
              <div className="aspect-video bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center">
                <div className="text-center text-white">
                  <TrendingUp className="w-12 h-12 mx-auto mb-2" />
                  <p className="font-medium">
                    Reportes de rendimiento completos
                  </p>
                </div>
              </div>
            </Card>

            {/* Screenshot 3 */}
            <Card className="overflow-hidden md:col-span-2 lg:col-span-1">
              <div className="aspect-video bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center">
                <div className="text-center text-white">
                  <Shield className="w-12 h-12 mx-auto mb-2" />
                  <p className="font-medium">Seguridad garantizada</p>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* BENEFITS SECTION */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Beneficios
            </h2>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {benefits.map((benefit, index) => (
              <BenefitCard
                key={index}
                icon={benefit.icon}
                title={benefit.title}
                description={benefit.description}
              />
            ))}
          </div>
        </div>
      </section>

      {/* TESTIMONIALS SECTION */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Testimonios
            </h2>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <TestimonialCard
                key={index}
                content={testimonial.content}
                author={testimonial.author}
                role={testimonial.role}
                rating={testimonial.rating}
              />
            ))}
          </div>
        </div>
      </section>

      {/* CTA SECTION */}
      <section className="py-20 bg-gradient-to-br from-blue-600 to-green-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl lg:text-4xl font-bold text-white mb-6">
            ¿Listo para mejorar tu relación con el dinero?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Únete a miles de usuarios que ya transformaron sus finanzas con
            FinTrack.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              variant="secondary"
              size="lg"
              onClick={handleDemoClick}
              loading={isCreating}
              className="bg-white text-blue-600 hover:bg-gray-50"
            >
              Probar demo gratuita ahora
            </Button>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="bg-slate-100 border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid md:grid-cols-4 gap-8">
            {/* Logo & Description */}
            <div className="md:col-span-2">
              <div className="flex items-center mb-4">
                <TrendingUp className="w-8 h-8 text-blue-600 mr-2" />
                <span className="text-xl font-bold text-gray-900">
                  FinTrack
                </span>
              </div>
              <p className="text-gray-600 mb-4">
                Toma el control de tus finanzas personales con la plataforma más
                intuitiva y completa del mercado.
              </p>
            </div>

            {/* Links */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-4">
                Política de privacidad
              </h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>
                  <a href="#" className="hover:text-blue-600 transition-colors">
                    Privacidad
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-blue-600 transition-colors">
                    Términos
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-blue-600 transition-colors">
                    Cookies
                  </a>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-gray-900 mb-4">Contacto</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>
                  <a href="#" className="hover:text-blue-600 transition-colors">
                    Soporte
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-blue-600 transition-colors">
                    FAQ
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-blue-600 transition-colors">
                    Blog
                  </a>
                </li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-200 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-500 text-sm">
              © 2025 FinTrack. Todos los derechos reservados.
            </p>

            {/* Social Links */}
            <div className="flex space-x-4 mt-4 md:mt-0">
              <a
                href="#"
                className="text-gray-400 hover:text-blue-600 transition-colors"
              >
                <Globe className="w-5 h-5" />
              </a>
              <a
                href="#"
                className="text-gray-400 hover:text-blue-600 transition-colors"
              >
                <Users className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
