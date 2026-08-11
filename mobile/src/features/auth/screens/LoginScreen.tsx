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
import { useLogin } from '../../../hooks/useAuth';
import { Ionicons } from '@expo/vector-icons';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email'),
  password: z.string().min(1, 'Password is required'),
});

type LoginFormData = z.infer<typeof loginSchema>;

type NavigationProp = NativeStackNavigationProp<AuthStackParamList, 'Login'>;

export default function LoginScreen() {
  const navigation = useNavigation<NavigationProp>();
  const { mutate: login, isPending } = useLogin();

  const { control, handleSubmit } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = (data: LoginFormData) => {
    login(data);
  };

  return (
    <ScreenLayout showBack>
      <View className="flex-1 pt-6 px-2">
        <Text className="text-3xl font-bold text-dark dark:text-white mb-2">
          Welcome Back
        </Text>
        <Text className="text-base text-gray-500 mb-8">
          Sign in to continue to PlanMinds.
        </Text>

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
              placeholder="Enter your password"
              secureTextEntry
              value={value}
              onChangeText={onChange}
              onBlur={onBlur}
              error={error?.message}
              leftIcon={<Ionicons name="lock-closed-outline" size={20} color="#94A3B8" />}
            />
          )}
        />

        <View className="items-end mb-8 mt-2">
          <TouchableOpacity onPress={() => navigation.navigate('ForgotPassword')}>
            <Text className="text-primary font-medium">Forgot Password?</Text>
          </TouchableOpacity>
        </View>

        <Button
          title="Sign In"
          onPress={handleSubmit(onSubmit)}
          loading={isPending}
          className="mb-8"
        />
        
        <View className="flex-row justify-center">
          <Text className="text-gray-500 dark:text-gray-400">Don't have an account? </Text>
          <TouchableOpacity onPress={() => navigation.replace('Register')}>
            <Text className="text-primary font-bold">Sign Up</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScreenLayout>
  );
}
