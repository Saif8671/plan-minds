import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import {
  exchangeFirebaseToken,
  fetchProfile,
  clearToken,
  setToken,
} from '../api';
import {
  createUserWithEmailAndPassword,
  firebaseAuth,
  googleProvider,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut as signOutFirebase,
  updateProfile,
} from '../lib/firebase';
import type { User } from '../types';

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  error: string | null;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, name?: string) => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  signOut: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

async function syncFirebaseSession() {
  const firebaseUser = firebaseAuth.currentUser;
  if (!firebaseUser) {
    clearToken();
    return null;
  }

  const idToken = await firebaseUser.getIdToken();
  const tokens = await exchangeFirebaseToken(idToken);
  setToken(tokens.access_token, tokens.refresh_token);
  return fetchProfile();
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshUser = async () => {
    try {
      setLoading(true);
      const profile = await fetchProfile();
      setUser(profile);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(firebaseAuth, async (firebaseUser) => {
      try {
        setLoading(true);

        if (!firebaseUser) {
          clearToken();
          setUser(null);
          return;
        }

        setError(null);
        const profile = await syncFirebaseSession();
        setUser(profile);
      } catch (err) {
        clearToken();
        setUser(null);
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    });

    return unsubscribe;
  }, []);

  const signIn = async (email: string, password: string) => {
    setError(null);
    try {
      await signInWithEmailAndPassword(firebaseAuth, email, password);
      const profile = await syncFirebaseSession();
      setUser(profile);
    } catch (err) {
      setError((err as Error).message);
      throw err;
    }
  };

  const signUp = async (email: string, password: string, name?: string) => {
    setError(null);
    try {
      const result = await createUserWithEmailAndPassword(
        firebaseAuth,
        email,
        password,
      );

      if (name) {
        await updateProfile(result.user, { displayName: name });
      }

      const profile = await syncFirebaseSession();
      setUser(profile);
    } catch (err) {
      setError((err as Error).message);
      throw err;
    }
  };

  const signInWithGoogle = async () => {
    setError(null);
    try {
      const result = await signInWithPopup(firebaseAuth, googleProvider);
      const idToken = await result.user.getIdToken();
      const tokens = await exchangeFirebaseToken(idToken);
      setToken(tokens.access_token, tokens.refresh_token);
      const profile = await fetchProfile();
      setUser(profile);
    } catch (err) {
      setError((err as Error).message);
      throw err;
    }
  };

  const signOut = () => {
    setError(null);
    void signOutFirebase(firebaseAuth);
    clearToken();
    setUser(null);
  };

  const value = useMemo(
    () => ({
      user,
      loading,
      error,
      signIn,
      signUp,
      signInWithGoogle,
      signOut,
      refreshUser,
    }),
    [user, loading, error],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
