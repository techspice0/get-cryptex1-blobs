# get-cryptex1-blobs

A streamlined script and workflow to retrieve `cryptex1` blobs for A9+ iOS devices.

## ⚠️ Compatibility
* **Supported:** A9 chips and newer (A9+).
* **Not Supported:** Apple TV 4, HomePod, and devices with chips older than A9.
* **Requirement:** The device must be **jailbroken**.

---

## 🛠️ Setup Instructions

### 1. Device Configuration
First, you need to install the necessary tools on your jailbroken device:

1.  Add the following repository to your package manager (Cydia, Sileo, Zebra):  
    `https://repo.049981.xyz`
2.  Navigate to the **x8A4** section within the repo.
3.  Install **every tweak** listed in that section.
4.  Ensure **OpenSSH** is installed on your device (usually available in default repos).

### 2. Retrieve the Encryption Key
From your computer, run the following command to grab the key from your device (replace `<ip>` and `<password>` with your device's details):

`bash
ssh mobile@<ip> "echo <password> | sudo -S x8A4 -k 0x8A4"`

|
|
Note: Look for the "KEY:" block in the response. Copy the string that follows it, but remove the 0x prefix.
