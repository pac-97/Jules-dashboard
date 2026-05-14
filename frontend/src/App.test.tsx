import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App', () => {
  it('renders the sidebar and executive dashboard by default', () => {
    render(<App />);
    expect(screen.getByText('AWS Security')).toBeInTheDocument();
  });
});
