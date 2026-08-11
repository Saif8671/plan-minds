import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { AuthStackParamList } from '../../../navigation/types';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { Button } from '../../../components/common/Button';
import { Input } from '../../../components/common/Input';
import { useRegister } from '../../../hooks/useAuth';
import { Ionicons } from '@expo/vector-icons';

const registerSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type RegisterFormData = z.infer<typeof registerSchema>;

type NavigationProp = NativeStackNavigationProp<AuthStackParamList, 'Register'>;

export default function RegisterScreen() {
  const navigation = useNavigation<NavigationProp>();
  const { mutate: register, isPending } = useRegister();

  const { control, handleSubmit } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
  });

  const onSubmit = (data: RegisterFormData) => {
    register({ email: data.email, password: data.password, name: data.name });
  };

  return (
    <ScreenLayout showBack scrollable keyboardAvoid>
      <View className="flex-1 pt-6 px-2">
        <Text className="text-3xl font-bold text-dark dark:text-white mb-2">
          Create Account
        </Text>
        <Text className="text-base text-gray-500 mb-8">
          Join PlanMinds to start scheduling smarter.
        </Text>

        <Controller
          control={control}
          name="name"
          render={({ field: { onChange, onBlur, value }, fieldState: { error } }) => (
            <Input
              label="Full Name"
              placeholder="Enter your name"
              value={value}
              onChangeText={onChange}
              onBlur={onBlur}
              error={error?.message}
              leftIcon={<Ionicons name="person-outline" size={20} color="#94A3B8" />}
            />
          )}
        />

        <Controller
          control={control}
          name="email"
          render={({ field: { onChange, onBlur, value }, fieldState: { error } }) => (
            <Input
              label="Email"
              placeholder="Enter your email"
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
              value={value}
              onChangeText={onChange}
              onBlur={onBlur}
              error={error?.message}
              leftIcon={<Ionicons name="mail-outline" size={20} color="#94A3B8" />}
            />
          )}
        />

        <Controller
          control={control}
          name="password"
          render={({ field: { onChange, onBlur, value }, fieldState: { error } }) => (
            <Input
              label="Password"
              placeholder="Create a password"
              secureTextEntry
              value={value}
              onChangeText={onChange}
              onBlur={onBlur}
              error={error?.message}
              leftIcon={<Ionicons name="lock-closed-outline" size={20} color="#94A3B8" />}
            />
          )}
        />

        <Controller
          control={control}
          name="confirmPassword"
          render={({ field: { onChange, onBlur, value }, fieldState: { error } }) => (
            <Input
              label="Confirm Password"
              placeholder="Repeat your password"
              secureTextEntry
              value={value}
              onChangeText={onChange}
              onBlur={onBlur}
              error={error?.message}
              leftIcon={<Ionicons name="lock-closed-outline" size={20} color="#94A3B8" />}
            />
          )}
        />

        <Button
          title="Sign Up"
          onPress={handleSubmit(onSubmit)}
          loading={isPending}
          className="mt-6 mb-8"
        />
        
        <View className="flex-row justify-center pb-8">
          <Text className="text-gray-500 dark:text-gray-400">Already have an account? </Text>
          <TouchableOpacity onPress={() => navigation.replace('Login')}>
            <Text className="text-primary font-bold">Sign In</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScreenLayout>
  );
}
