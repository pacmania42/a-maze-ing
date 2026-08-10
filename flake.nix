{
  description = "Nix flake for a-maze-ing";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      systems = nixpkgs.lib.systems.flakeExposed;
      forEachSystem = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in
    {
      devShells = forEachSystem (pkgs: {
        default =
          let
            x11Libs = with pkgs; [
              libX11
              libXrandr
              libXrender
              libXext
              libXcursor
              libXinerama
              libXi
              libXxf86vm
              libxcb
              libxcb-keysyms
            ];
            glLibs = with pkgs; [
              libGL
              vulkan-tools
              vulkan-validation-layers
              vulkan-loader
            ];
            fontLibs = with pkgs; [
              freetype
              fontconfig
            ];
            zLibs = with pkgs; [
              zlib
            ];
            bsdLibs = with pkgs; [
              libbsd
            ];
          in
          pkgs.mkShellNoCC {
            packages = [
              pkgs.python313
              pkgs.uv
              pkgs.ruff
            ]
            ++ glLibs
            ++ x11Libs
            ++ fontLibs
            ++ zLibs
            ++ bsdLibs;
            env = {
              LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath (
                [ pkgs.stdenv.cc.cc.lib ] ++ glLibs ++ x11Libs ++ fontLibs ++ zLibs ++ bsdLibs
              );
              UV_PYTHON_DOWNLOADS = "never";
              UV_PYTHON = "${pkgs.python313}/bin/python3.13";
            };
          };
      });
    };
}
