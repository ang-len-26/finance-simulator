// =====================================================
// BUTTON COMPONENT - Sistema completo de botones
// Implementa todos los estilos definidos en components.css
// =====================================================

import React, { ButtonHTMLAttributes, ReactNode } from "react";
import { Loader2 } from "lucide-react";

// =====================================================
// TYPES
// =====================================================

export type ButtonVariant =
  | "primary"
  | "secondary"
  | "outline"
  | "ghost"
  | "sidebar"
  | "navbar";

export type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  children: ReactNode;
  className?: string;
}

// =====================================================
// SIZE STYLES
// =====================================================

const sizeStyles = {
  sm: "px-3 py-1.5 text-sm rounded-md",
  md: "px-4 py-2 text-sm rounded-lg",
  lg: "px-6 py-3 text-base rounded-lg",
};

// =====================================================
// BUTTON COMPONENT
// =====================================================

export const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  size = "md",
  loading = false,
  leftIcon,
  rightIcon,
  children,
  disabled,
  className = "",
  ...props
}) => {
  // Base classes
  const baseClasses = `
    inline-flex items-center justify-center gap-2
    font-medium transition-all duration-200 ease-in-out
    focus:outline-none focus:ring-2 focus:ring-offset-2
    disabled:cursor-not-allowed disabled:transform-none
    ${sizeStyles[size]}
  `
    .trim()
    .replace(/\s+/g, " ");

  // Variant classes (usa las clases CSS definidas)
  const variantClasses = {
    primary: "btn-primary focus:ring-btn-primary-default",
    secondary: "btn-secondary focus:ring-btn-secondary-default",
    outline: "btn-outline focus:ring-btn-primary-default",
    ghost: "btn-ghost focus:ring-gray-300",
    sidebar: "btn-sidebar focus:ring-gray-300",
    navbar: "btn-navbar focus:ring-gray-300",
  };

  const buttonClasses = `
    ${baseClasses}
    ${variantClasses[variant]}
    ${className}
  `
    .trim()
    .replace(/\s+/g, " ");

  return (
    <button className={buttonClasses} disabled={disabled || loading} {...props}>
      {/* Loading spinner */}
      {loading && <Loader2 className="w-4 h-4 animate-spin" />}

      {/* Left icon */}
      {!loading && leftIcon && (
        <span className="flex-shrink-0">{leftIcon}</span>
      )}

      {/* Button text */}
      <span>{children}</span>

      {/* Right icon */}
      {!loading && rightIcon && (
        <span className="flex-shrink-0">{rightIcon}</span>
      )}
    </button>
  );
};

// =====================================================
// BUTTON VARIANTS - Componentes preconfigurados
// =====================================================

export const PrimaryButton: React.FC<Omit<ButtonProps, "variant">> = (
  props
) => <Button variant="primary" {...props} />;

export const SecondaryButton: React.FC<Omit<ButtonProps, "variant">> = (
  props
) => <Button variant="secondary" {...props} />;

export const OutlineButton: React.FC<Omit<ButtonProps, "variant">> = (
  props
) => <Button variant="outline" {...props} />;

export const GhostButton: React.FC<Omit<ButtonProps, "variant">> = (props) => (
  <Button variant="ghost" {...props} />
);

// =====================================================
// ICON BUTTON - Para botones solo con icono
// =====================================================

export interface IconButtonProps
  extends Omit<ButtonProps, "children" | "leftIcon" | "rightIcon"> {
  icon: ReactNode;
  "aria-label": string;
}

export const IconButton: React.FC<IconButtonProps> = ({
  icon,
  size = "md",
  ...props
}) => {
  const iconSizes = {
    sm: "w-4 h-4",
    md: "w-5 h-5",
    lg: "w-6 h-6",
  };

  const paddingSizes = {
    sm: "p-1.5",
    md: "p-2",
    lg: "p-3",
  };

  return (
    <Button
      size={size}
      className={`${paddingSizes[size]} aspect-square`}
      {...props}
    >
      <span className={iconSizes[size]}>{icon}</span>
    </Button>
  );
};

// =====================================================
// BUTTON GROUP - Para agrupar botones
// =====================================================

export interface ButtonGroupProps {
  children: ReactNode;
  className?: string;
}

export const ButtonGroup: React.FC<ButtonGroupProps> = ({
  children,
  className = "",
}) => <div className={`inline-flex rounded-lg ${className}`}>{children}</div>;

export default Button;
