# Dria Network Mintlify Documentation

This directory contains the source files for the Dria Network documentation, built with Mintlify.

## Prerequisites

Before you can run the documentation locally, you need to have Node.js and npm (or yarn) installed on your system.

- **Node.js**: Download and install from [nodejs.org](https://nodejs.org/)
- **npm**: Comes with Node.js.
- (Optional) **yarn**: Install via `npm install --global yarn` if you prefer yarn.

## Setup

1.  **Install Mintlify CLI:**
    Open your terminal and run the following command to install the Mintlify command-line interface globally:
    ```bash
    npm install -g mintlify
    ```
    Or, if you prefer yarn:
    ```bash
    yarn global add mintlify
    ```

2.  **Install Project Dependencies (Optional but Recommended for Future Customizations):
**
    While not strictly necessary for just running `mintlify dev` with a basic setup, if you plan to add custom components or themes later, you might want to initialize a `package.json`.
    ```bash
    npm init -y
    # Then you could add mintlify as a dev dependency if you wish, though the global install is often sufficient for building/developing.
    # npm install mintlify --save-dev
    ```

## Running Locally

1.  **Navigate to your workspace root directory** (where the `mint.json` file is located) in your terminal.

2.  **Run the Mintlify development server:**
    ```bash
    mintlify dev
    ```
    This command will start a local development server (usually on `http://localhost:3000`) and open the documentation site in your default web browser. The server will automatically reload when you make changes to your markdown files or `mint.json`.

## File Structure

-   `mint.json`: The main configuration file for your Mintlify site. This defines navigation, appearance, and other settings.
-   `docs/`: This directory contains your actual documentation content.
    -   `overview.mdx`: The main page for your tokenomics documentation.
-   `README.md`: This file, providing setup and run instructions.

## Customization

-   **Logos & Favicon**: Update the paths in `mint.json` and add your actual logo (`logo-light.svg`, `logo-dark.svg`) and favicon (`favicon.png`) files to a `public/` directory in your workspace root (e.g., `public/logo-light.svg`). Create the `public` directory if it doesn't exist.
-   **Navigation**: Modify the `navigation` array in `mint.json` to add more pages or sections.
-   **Styling**: Refer to the [Mintlify documentation](https://mintlify.com/docs) for more advanced customization options, theming, and adding custom components.

## Building for Production

When you're ready to deploy your documentation, you can build a static version using:
```bash
mintlify build
```
This will generate a `site` directory (or `.mintlify/build` depending on version/config) containing the static files for your documentation, which you can then deploy to any static hosting service (e.g., Vercel, Netlify, GitHub Pages). 