import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import LoginScreen     from './src/screens/LoginScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import GenerateScreen  from './src/screens/GenerateScreen';
import PreviewScreen   from './src/screens/PreviewScreen';
import ProfileScreen   from './src/screens/ProfileScreen';

export type RootStackParamList = {
  Login:     undefined;
  Dashboard: undefined;
  Generate:  { module?: string };
  Preview:   { result: object };
  Profile:   undefined;
};

const Stack = createStackNavigator<RootStackParamList>();

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName="Login"
          screenOptions={{
            headerStyle:   { backgroundColor: '#0b1020' },
            headerTintColor: '#e2e8f0',
            headerTitleStyle: { fontWeight: '700' },
            cardStyle:     { backgroundColor: '#0b1020' },
          }}
        >
          <Stack.Screen name="Login"     component={LoginScreen}     options={{ headerShown: false }} />
          <Stack.Screen name="Dashboard" component={DashboardScreen} options={{ title: '✦ Easy AI' }} />
          <Stack.Screen name="Generate"  component={GenerateScreen}  options={{ title: 'Generate' }} />
          <Stack.Screen name="Preview"   component={PreviewScreen}   options={{ title: 'Preview' }} />
          <Stack.Screen name="Profile"   component={ProfileScreen}   options={{ title: 'Profile' }} />
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}
