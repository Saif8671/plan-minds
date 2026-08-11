import React from 'react';
import {
  TouchableOpacity,
  Text,
  ActivityIndicator,
  StyleSheet,
  ViewStyle,
  TextStyle,
  TouchableOpacityProps,
} from 'react-native';
import { cn } from '../../utils/cn';

export interface ButtonProps extends TouchableOpacityProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  title: string;
  className?: string;
  textClassName?: string;
}

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled,
  title,
  leftIcon,
  rightIcon,
  className,
  textClassName,
  ...props
}: ButtonProps) {
  const baseClasses = "flex-row items-center justify-center rounded-xl";
  
  const variantClasses = {
    primary: "bg-primary",
    secondary: "bg-secondary",
    outline: "border-2 border-primary bg-transparent",
    ghost: "bg-transparent",
    danger: "bg-error",
  };
  
  const sizeClasses = {
    sm: "px-3 py-2",
    md: "px-4 py-3",
    lg: "px-6 py-4",
  };
  
  const disabledClasses = (disabled || loading) ? "opacity-50" : "";
  
  const textBaseClasses = "font-semibold text-center";
  const textVariantClasses = {
    primary: "text-white",
    secondary: "text-white",
    outline: "text-primary",
    ghost: "text-primary",
    danger: "text-white",
  };
  
  const textSizeClasses = {
    sm: "text-sm",
    md: "text-base",
    lg: "text-lg",
  };

  return (
    <TouchableOpacity
      activeOpacity={0.7}
      disabled={disabled || loading}
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        disabledClasses,
        className
      )}
      {...props}
    >
      {loading ? (
        <ActivityIndicator
          size="small"
          color={variant === 'outline' || variant === 'ghost' ? '#1677FF' : '#fff'}
        />
      ) : (
        <>
          {leftIcon && <React.Fragment>{leftIcon}</React.Fragment>}
          <Text
            className={cn(
              textBaseClasses,
              textVariantClasses[variant],
              textSizeClasses[size],
              leftIcon ? "ml-2" : "",
              rightIcon ? "mr-2" : "",
              textClassName
            )}
          >
            {title}
          </Text>
          {rightIcon && <React.Fragment>{rightIcon}</React.Fragment>}
        </>
      )}
    </TouchableOpacity>
  );
}
