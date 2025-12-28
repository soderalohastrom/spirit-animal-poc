import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error: unknown;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

const serializeError = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  try {
    return JSON.stringify(error, null, 2);
  } catch {
    return 'An unknown error occurred';
  }
};

const getErrorStack = (error: unknown): string | null => {
  if (error instanceof Error && error.stack) {
    return error.stack;
  }
  return null;
};

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: unknown): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: unknown, errorInfo: React.ErrorInfo): void {
    // Log error to console in development, could send to error tracking service in production
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      const errorMessage = serializeError(this.state.error);
      const errorStack = getErrorStack(this.state.error);
      const isDevelopment = import.meta.env.DEV;

      return (
        <div className="min-h-[200px] flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-white border border-red-200 rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <title>Error icon</title>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h2 className="text-lg font-semibold text-gray-900">Something went wrong</h2>
            </div>
            
            <p className="text-gray-600 mb-4">
              We encountered an unexpected error. Please try again.
            </p>

            {isDevelopment && (
              <details className="mb-4">
                <summary className="text-sm text-gray-500 cursor-pointer hover:text-gray-700">
                  Technical details
                </summary>
                <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm font-mono text-red-600 break-words">{errorMessage}</p>
                  {errorStack && (
                    <pre className="mt-2 text-xs text-gray-500 overflow-auto max-h-32">
                      {errorStack}
                    </pre>
                  )}
                </div>
              </details>
            )}

            <button
              type="button"
              onClick={this.handleReset}
              className="w-full py-2 px-4 bg-purple-500 text-white rounded-lg font-medium hover:bg-purple-600 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
