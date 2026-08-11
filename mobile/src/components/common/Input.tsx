import React, { forwardRef, useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TextInputProps,
  TouchableOpacity,
} from 'react-native';
import { cn } from '../../utils/cn';
import { Ionicons } from '@expo/vector-icons';

export interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  containerClassName?: string;
  inputClassName?: string;
}

export const Input = forwardRef<TextInput, InputProps>(
  (
    {
      label,
      error,
      leftIcon,
      rightIcon,
      containerClassName,
      inputClassName,
      secureTextEntry,
      className,
      ...props
    },
    ref
  ) => {
    const [isFocused, setIsFocused] = useState(false);
    const [isPasswordVisible, setIsPasswordVisible] = useState(false);

    const isPassword = secureTextEntry !== undefined;

    return (
      <View className={cn('mb-4 w-full', containerClassName)}>
        {label && (
          <Text className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
            {label}
          </Text>
        )}
        <View
          className={cn(
            'flex-row items-center rounded-xl border bg-gray-50 px-4 py-3 dark:bg-gray-800',
            isFocused
              ? 'border-primary'
              : error
              ? 'border-error'
              : 'border-gray-200 dark:border-gray-700',
            className
          )}
        >
          {leftIcon && <View className="mr-3">{leftIcon}</View>}
          <TextInput
            ref={ref}
            className={cn(
              'flex-1 text-base text-dark dark:text-white',
              inputClassName
            )}
            placeholderTextColor="#94A3B8"
            onFocus={(e) => {
              setIsFocused(true);
              props.onFocus?.(e);
            }}
            onBlur={(e) => {
              setIsFocused(false);
              props.onBlur?.(e);
            }}
            secureTextEntry={isPassword && !isPasswordVisible}
            {...props}
          />
          {rightIcon && !isPassword && <View className="ml-3">{rightIcon}</View>}
          {isPassword && (
            <TouchableOpacity
              className="ml-3"
              onPress={() => setIsPasswordVisible(!isPasswordVisible)}
            >
              <Ionicons
                name={isPasswordVisible ? 'eye-off-outline' : 'eye-outline'}
                size={20}
                color="#94A3B8"
              />
            </TouchableOpacity>
          )}
        </View>
        {error && (
          <Text className="mt-1 text-xs text-error">
            {error}
          </Text>
        )}
      </View>
    );
  }
);

Input.displayName = 'Input';
