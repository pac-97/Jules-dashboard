import '@testing-library/jest-dom';
import { ResizeObserver } from 'resize-observer';

window.ResizeObserver = ResizeObserver as any;
