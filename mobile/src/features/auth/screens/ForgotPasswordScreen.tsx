import React from 'react';
import { View, Text } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { AuthStackParamList } from '../../../navigation/types';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { Button } from '../../../components/common/Button';
import { Input } from '../../../components/common/Input';
import { useForgotPassword } from '../../../hooks/useAuth';
import { Ionicons } from '@expo/vector-icons';

const forgotPasswordSchema = z.object({
  email: z.string().email('Please enter a valid email'),
});

type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;
type NavigationProp = NativeStackNavigationProp<AuthStackParamList, 'ForgotPassword'>;

export default function ForgotPasswordScreen() {
  const navigation = useNavigation<NavigationProp>();
  const { mutate: forgotPassword, isPending } = useForgotPassword();

  const { control, handleSubmit } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: '' },
  });

  const onSubmit = (data: ForgotPasswordFormData) => {
    forgotPassword(data.email, {
      onSuccess: () => {
        navigation.navigate('OTPVerification', { email: data.email });
      }
    });
  };

  return (
    <ScreenLayout showBack>
      <View className="flex-1 pt-6 px-2">
        <Text className="text-3xl font-bold text-dark dark:text-white mb-2">
          Forgot Password
        </Text>
        <Text className="text-base text-gray-500 mb-8">
          Enter your email address and we'll send you a 6-digit code to reset your password.
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

        <Button
          title="Send Reset Code"
          onPress={handleSubmit(onSubmit)}
          loading={isPending}
          className="mt-6"
        />
      </View>
    </ScreenLayout>
  );
}
