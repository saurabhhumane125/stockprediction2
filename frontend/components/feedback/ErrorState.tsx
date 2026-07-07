interface ErrorStateProps {
  message: string;
}

export function ErrorState({
  message,
}: Readonly<ErrorStateProps>) {
  return (
    <div className="rounded-2xl border border-red-200 bg-red-50 p-8">
      <h2 className="mb-2 text-lg font-semibold text-red-700">
        Something went wrong
      </h2>

      <p className="text-red-600">
        {message}
      </p>
    </div>
  );
}