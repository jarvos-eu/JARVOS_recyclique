export function PlaceholderPage({ title, testId }: { title: string; testId: string }) {
  return (
    <div data-testid={testId}>
      <h1>{title}</h1>
    </div>
  );
}
