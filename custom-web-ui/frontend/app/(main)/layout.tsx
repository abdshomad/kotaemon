export default function MainLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="flex min-h-full flex-1 flex-col">
      <header className="border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
        <span className="text-sm font-medium text-zinc-800 dark:text-zinc-100">
          Kotaemon
        </span>
      </header>
      {children}
    </div>
  );
}
