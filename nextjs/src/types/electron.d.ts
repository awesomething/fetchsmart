export {};

declare global {
  interface Window {
    electronAPI?: {
      openFloatingWindow: (
        url: string,
        options?: {
          width?: number;
          height?: number;
          alwaysOnTop?: boolean;
          frame?: boolean;
          resizable?: boolean;
        }
      ) => Promise<number>;
      closeFloatingWindow: (windowId: number) => Promise<void>;
      listFloatingWindows: () => Promise<Array<{ id: number; url: string }>>;
      isElectron: () => boolean;
    };
  }
}

