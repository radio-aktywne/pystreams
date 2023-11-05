{
  inputs = {
    nixpkgs = {
      url = "github:NixOS/nixpkgs/nixos-unstable";
    };

    flake-parts = {
      url = "github:hercules-ci/flake-parts";
    };
  };

  outputs = inputs:
    inputs.flake-parts.lib.mkFlake {inherit inputs;} {
      # Import local override if it exists
      imports = [
        (
          if builtins.pathExists ./local.nix
          then ./local.nix
          else {}
        )
      ];

      # Sensible defaults
      systems = [
        "x86_64-linux"
        "i686-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      perSystem = {
        config,
        pkgs,
        system,
        ...
      }: let
        node = pkgs.nodejs;
        python = pkgs.python311;
        nil = pkgs.nil;
        task = pkgs.go-task;
        coreutils = pkgs.coreutils;
        trunk = pkgs.trunk-io;
        poetry = pkgs.poetry;
        copier = pkgs.copier;
        ffmpeg = pkgs.ffmpeg;
        s5cmd = pkgs.s5cmd;
      in {
        # Override pkgs argument
        _module.args.pkgs = import inputs.nixpkgs {
          inherit system;
          config = {
            # Allow packages with non-free licenses
            allowUnfree = true;
            # Allow packages with broken dependencies
            allowBroken = true;
            # Allow packages with unsupported system
            allowUnsupportedSystem = true;
          };
        };

        # Set which formatter should be used
        formatter = pkgs.alejandra;

        # Define multiple development shells for different purposes
        devShells = {
          default = pkgs.mkShell {
            name = "dev";

            packages = [
              node
              python
              nil
              task
              coreutils
              trunk
              poetry
              copier
              ffmpeg
              s5cmd
            ];

            shellHook = ''
              task install
              source .venv/bin/activate
            '';
          };

          package = pkgs.mkShell {
            name = "package";

            packages = [
              python
              task
              coreutils
              poetry
            ];

            shellHook = ''
              task install
              source .venv/bin/activate
            '';
          };

          template = pkgs.mkShell {
            name = "template";

            packages = [
              task
              coreutils
              copier
            ];
          };

          lint = pkgs.mkShell {
            name = "lint";

            packages = [
              node
              task
              coreutils
              trunk
            ];
          };

          test = pkgs.mkShell {
            name = "test";

            packages = [
              python
              task
              coreutils
              poetry
              ffmpeg
              s5cmd
            ];

            shellHook = ''
              task install
              source .venv/bin/activate
            '';
          };

          docs = pkgs.mkShell {
            name = "docs";

            packages = [
              node
              task
              coreutils
            ];
          };
        };
      };
    };
}
