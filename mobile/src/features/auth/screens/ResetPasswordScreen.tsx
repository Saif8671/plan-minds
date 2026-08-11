import React from 'react';
import { View, Text } from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { AuthStackParamList } from '../../../navigation/types';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { Button } from '../../../components/common/Button';
import { Input } from '../../../components/common/Input';
import { useResetPassword } from '../../../hooks/useAuth';
import { Ionicons } from '@expo/vector-icons';

const resetPasswordSchema = z.object({
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;
type NavigationProp = NativeStackNavigationProp<AuthStackParamList, 'ResetPassword'>;
type RouteType = RouteProp<AuthStackParamList, 'ResetPassword'>;

export default function ResetPasswordScreen() {
  const navigation = useNavigation<NavigationProp>();
  const route = useRoute<RouteType>();
  const { token } = route.params;

  const { mutate: resetPassword, isPending } = useResetPassword();

  const { control, handleSubmit } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: { password: '', confirmPassword: '' },
  });

  const onSubmit = (data: ResetPasswordFormData) => {
    resetPassword({ token, password: data.password }, {
      onSuccess: () => {
        // Reset navigation stack to Login
        navigation.reset({
          index: 0,
          routes: [{ name: 'Login' }],
        });
      }
    });
  };

  return (
    <ScreenLayout showBack>
      <View className="flex-1 pt-6 px-2">
        <Text className="text-3xl font-bold text-dark dark:text-white mb-2">
          New Password
        </Text>
        <Text className="text-base text-gray-500 mb-8">
          Create a new password for your account.
        </Text>

        <Controller
          control={control}
          name="password"
          render={({ field: { onChange, onBlur, value }, fieldState: { error } }) => (
            <Input
              label="New Password"
              placeholder="Enter new password"
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
              label="Confirm New Password"
              placeholder="Repeat new password"
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
          title="Reset Password"
          onPress={handleSubmit(onSubmit)}
          loading={isPending}
          className="mt-6"
        />
      </View>
    </ScreenLayout>
  );
}
