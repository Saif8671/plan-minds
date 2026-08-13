// Polyfill DOMException for React Native (Hermes doesn't provide it)
if (typeof globalThis.DOMException === 'undefined') {
  function DOMExceptionPolyfill(this: any, message?: string, name?: string) {
    const err = new Error(message || '');
    err.name = name || 'DOMException';
    Object.setPrototypeOf(err, DOMExceptionPolyfill.prototype);
    return err;
  }
  DOMExceptionPolyfill.prototype = Object.create(Error.prototype);
  DOMExceptionPolyfill.prototype.constructor = DOMExceptionPolyfill;
  (globalThis as any).DOMException = DOMExceptionPolyfill;
}

import { registerRootComponent } from 'expo';

import App from './App';

// registerRootComponent calls AppRegistry.registerComponent('main', () => App);
// It also ensures that whether you load the app in Expo Go or in a native build,
// the environment is set up appropriately
registerRootComponent(App);
