import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { cn } from '../../utils/cn';

interface SearchBarProps {
  value: string;
  onChangeText: (text: string) => void;
  placeholder?: string;
  onClear?: () => void;
  className?: string;
}

export function SearchBar({
  value,
  onChangeText,
  placeholder = 'Search...',
  onClear,
  className,
}: SearchBarProps) {
  const [isFocused, setIsFocused] = useState(false);

  const handleClear = () => {
    onChangeText('');
    if (onClear) onClear();
  };

  return (
    <View
      className={cn(
        'flex-row items-center rounded-xl bg-gray-100 px-3 py-2 dark:bg-gray-800',
        isFocused ? 'border border-primary bg-white dark:bg-gray-900' : 'border border-transparent',
        className
      )}
    >
      <Ionicons name="search" size={20} color={isFocused ? '#1677FF' : '#94A3B8'} />
      <TextInput
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor="#94A3B8"
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        className="ml-2 flex-1 text-base text-dark dark:text-white"
        returnKeyType="search"
      />
      {value.length > 0 && (
        <TouchableOpacity onPress={handleClear} className="ml-2 p-1">
          <Ionicons name="close-circle" size={18} color="#94A3B8" />
        </TouchableOpacity>
      )}
    </View>
  );
}
