import React, { useState, useRef, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity } from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { AuthStackParamList } from '../../../navigation/types';
import { ScreenLayout } from '../../../components/layouts/ScreenLayout';
import { Button } from '../../../components/common/Button';
import { useVerifyOTP, useForgotPassword } from '../../../hooks/useAuth';
import { cn } from '../../../utils/cn';

type NavigationProp = NativeStackNavigationProp<AuthStackParamList, 'OTPVerification'>;
type RouteType = RouteProp<AuthStackParamList, 'OTPVerification'>;

export default function OTPVerificationScreen() {
  const navigation = useNavigation<NavigationProp>();
  const route = useRoute<RouteType>();
  const { email } = route.params;
  
  const { mutate: verifyOTP, isPending } = useVerifyOTP();
  const { mutate: resendOTP, isPending: isResending } = useForgotPassword();

  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [timer, setTimer] = useState(60);
  const inputs = useRef<TextInput[]>([]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (timer > 0) {
      interval = setInterval(() => setTimer((t) => t - 1), 1000);
    }
    return () => clearInterval(interval);
  }, [timer]);

  const handleChange = (text: string, index: number) => {
    const newOtp = [...otp];
    newOtp[index] = text;
    setOtp(newOtp);

    // Auto-advance
    if (text.length === 1 && index < 5) {
      inputs.current[index + 1]?.focus();
    }

    // Auto-submit
    if (text.length === 1 && index === 5) {
      handleVerify(newOtp.join(''));
    }
  };

  const handleKeyPress = (e: any, index: number) => {
    if (e.nativeEvent.key === 'Backspace' && otp[index] === '' && index > 0) {
      inputs.current[index - 1]?.focus();
    }
  };

  const handleVerify = (code?: string) => {
    const finalCode = code || otp.join('');
    if (finalCode.length === 6) {
      verifyOTP({ email, otp: finalCode }, {
        onSuccess: () => {
          // Pass a dummy token since verifyOTP doesn't return one in this mock
          navigation.navigate('ResetPassword', { token: 'mock_token_123' });
        }
      });
    }
  };

  const handleResend = () => {
    if (timer > 0) return;
    resendOTP(email, {
      onSuccess: () => setTimer(60)
    });
  };

  return (
    <ScreenLayout showBack>
      <View className="flex-1 pt-6 px-2">
        <Text className="text-3xl font-bold text-dark dark:text-white mb-2">
          Verify Email
        </Text>
        <Text className="text-base text-gray-500 mb-8">
          We've sent a 6-digit code to {email}. Enter it below to verify your identity.
        </Text>

        <View className="flex-row justify-between mb-8">
          {otp.map((digit, index) => (
            <TextInput
              key={index}
              ref={(ref) => {
                if (ref) inputs.current[index] = ref;
              }}
              value={digit}
              onChangeText={(text) => handleChange(text, index)}
              onKeyPress={(e) => handleKeyPress(e, index)}
              keyboardType="number-pad"
              maxLength={1}
              className={cn(
                "w-12 h-14 border rounded-xl text-center text-2xl font-bold text-dark dark:text-white bg-gray-50 dark:bg-gray-800",
                digit ? "border-primary" : "border-gray-200 dark:border-gray-700"
              )}
            />
          ))}
        </View>

        <Button
          title="Verify Code"
          onPress={() => handleVerify()}
          loading={isPending}
          disabled={otp.join('').length !== 6}
          className="mb-8"
        />

        <View className="flex-row justify-center items-center">
          <Text className="text-gray-500 dark:text-gray-400">Didn't receive the code? </Text>
          <TouchableOpacity onPress={handleResend} disabled={timer > 0 || isResending}>
            <Text className={cn("font-bold", timer > 0 ? "text-gray-400" : "text-primary")}>
              {timer > 0 ? `Resend in ${timer}s` : "Resend Code"}
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScreenLayout>
  );
}
