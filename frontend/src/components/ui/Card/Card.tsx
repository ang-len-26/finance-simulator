// =====================================================
// CARD COMPONENT - Sistema completo de cards
// Implementa los estilos definidos en components.css
// =====================================================

import React, { ReactNode, HTMLAttributes } from "react";

// =====================================================
// TYPES
// =====================================================

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  hover?: boolean;
  className?: string;
}

export interface CardHeaderProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  className?: string;
}

export interface CardBodyProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  className?: string;
}

export interface CardFooterProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  className?: string;
}

// =====================================================
// CARD COMPONENT
// =====================================================

export const Card: React.FC<CardProps> = ({
  children,
  hover = true,
  className = "",
  ...props
}) => {
  const cardClasses = `
    card
    ${hover ? "transition-all duration-200 ease-in-out" : ""}
    ${className}
  `
    .trim()
    .replace(/\s+/g, " ");

  return (
    <div className={cardClasses} {...props}>
      {children}
    </div>
  );
};

// =====================================================
// CARD HEADER
// =====================================================

export const CardHeader: React.FC<CardHeaderProps> = ({
  children,
  className = "",
  ...props
}) => (
  <div className={`card-header ${className}`} {...props}>
    {children}
  </div>
);

// =====================================================
// CARD BODY
// =====================================================

export const CardBody: React.FC<CardBodyProps> = ({
  children,
  className = "",
  ...props
}) => (
  <div className={`card-body ${className}`} {...props}>
    {children}
  </div>
);

// =====================================================
// CARD FOOTER
// =====================================================

export const CardFooter: React.FC<CardFooterProps> = ({
  children,
  className = "",
  ...props
}) => (
  <div className={`card-footer ${className}`} {...props}>
    {children}
  </div>
);

// =====================================================
// CARD VARIANTS - Tarjetas preconfiguradas
// =====================================================

export interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  className?: string;
}

export const FeatureCard: React.FC<FeatureCardProps> = ({
  icon,
  title,
  description,
  className = "",
}) => (
  <Card className={`p-6 text-center ${className}`}>
    <div className="flex justify-center mb-4">
      <div className="w-12 h-12 flex items-center justify-center rounded-lg bg-btn-primary-default text-white">
        {icon}
      </div>
    </div>
    <CardHeader className="p-0 border-none">
      <h3 className="text-lg font-semibold text-text-primary mb-2">{title}</h3>
    </CardHeader>
    <CardBody className="p-0">
      <p className="text-text-secondary leading-relaxed">{description}</p>
    </CardBody>
  </Card>
);

// =====================================================
// TESTIMONIAL CARD
// =====================================================

export interface TestimonialCardProps {
  content: string;
  author: string;
  role?: string;
  avatar?: string;
  rating?: number;
  className?: string;
}

export const TestimonialCard: React.FC<TestimonialCardProps> = ({
  content,
  author,
  role,
  avatar,
  rating = 5,
  className = "",
}) => (
  <Card className={`p-6 ${className}`}>
    <CardBody className="p-0">
      {/* Rating */}
      {rating && (
        <div className="flex mb-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <span
              key={i}
              className={`text-lg ${
                i < rating ? "text-yellow-400" : "text-gray-300"
              }`}
            >
              ★
            </span>
          ))}
        </div>
      )}

      {/* Content */}
      <blockquote className="text-text-secondary mb-4 leading-relaxed">
        "{content}"
      </blockquote>

      {/* Author */}
      <div className="flex items-center">
        {avatar ? (
          <img
            src={avatar}
            alt={author}
            className="w-10 h-10 rounded-full mr-3"
          />
        ) : (
          <div className="w-10 h-10 bg-btn-primary-default rounded-full flex items-center justify-center mr-3">
            <span className="text-white font-medium">{author.charAt(0)}</span>
          </div>
        )}
        <div>
          <div className="font-medium text-text-primary">{author}</div>
          {role && <div className="text-sm text-text-secondary">{role}</div>}
        </div>
      </div>
    </CardBody>
  </Card>
);

// =====================================================
// BENEFIT CARD
// =====================================================

export interface BenefitCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  className?: string;
}

export const BenefitCard: React.FC<BenefitCardProps> = ({
  icon,
  title,
  description,
  className = "",
}) => (
  <Card className={`p-6 text-left ${className}`} hover={false}>
    <div className="flex items-start">
      <div className="flex-shrink-0 mr-4">
        <div className="w-8 h-8 flex items-center justify-center rounded-full bg-green-100 text-btn-secondary-default">
          {icon}
        </div>
      </div>
      <div>
        <h4 className="font-medium text-text-primary mb-2">{title}</h4>
        <p className="text-sm text-text-secondary">{description}</p>
      </div>
    </div>
  </Card>
);

// =====================================================
// STAT CARD - Para métricas
// =====================================================

export interface StatCardProps {
  value: string | number;
  label: string;
  change?: {
    value: number;
    type: "increase" | "decrease";
  };
  icon?: ReactNode;
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  value,
  label,
  change,
  icon,
  className = "",
}) => (
  <Card className={`p-6 ${className}`}>
    <div className="flex items-center justify-between">
      <div>
        <p className="text-2xl font-bold text-text-primary">{value}</p>
        <p className="text-sm text-text-secondary">{label}</p>
        {change && (
          <div
            className={`flex items-center mt-2 text-xs ${
              change.type === "increase"
                ? "text-state-success"
                : "text-state-error"
            }`}
          >
            <span>{change.type === "increase" ? "↗" : "↘"}</span>
            <span className="ml-1">{Math.abs(change.value)}%</span>
          </div>
        )}
      </div>
      {icon && <div className="text-btn-primary-default">{icon}</div>}
    </div>
  </Card>
);

export default Card;
