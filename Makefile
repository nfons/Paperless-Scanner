# Makefile for Paperless Scanner Application

# Default target
all: build

# Build the executable using PyInstaller
build:
	pyinstaller app.py -n paperless-scanner --icon icon.ico

build-osx:
	pyinstaller app.py -n paperless-scanner --icon icon.ico --osx-bundle-identifier com.nfons.paperlessscanner

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.spec

# Clean and rebuild
rebuild: clean build

# Install PyInstaller if not already installed
install-pyinstaller:
	pip install pyinstaller

# Full setup: install dependencies and build
setup: install-pyinstaller build

.PHONY: all build clean rebuild install-pyinstaller setup 