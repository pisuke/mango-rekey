#!/usr/bin/env python3

import json
import os

from absl import app
from absl import flags
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

FLAGS = flags.FLAGS

flags.DEFINE_string("i", None, "Input JSON file to modify.")
flags.DEFINE_string("o", None, "Output JSON file to write the changes.")
flags.mark_flag_as_required("i")
flags.mark_flag_as_required("o")

def generate_rsa_keypair(key_size=2048):
  """Generates an RSA key pair.

  Args:
      key_size: The size of the RSA key in bits (default: 2048).

  Returns:
      A tuple containing the private key and public key.
  """
  private_key = rsa.generate_private_key(
      public_exponent=65537,
      key_size=key_size,
  )
  public_key = private_key.public_key()
  return private_key, public_key

def save_keypair(private_key, public_key, device_name):
  """Saves the RSA key pair to files in a device-specific directory.

  Args:
    private_key: The RSA private key.
    public_key: The RSA public key.
    device_name: The name of the device (used for directory naming).
  """
  # Create the 'devices' directory if it doesn't exist
  os.makedirs("devices", exist_ok=True)

  # Create a directory for the device
  device_dir = os.path.join("devices", device_name)
  os.makedirs(device_dir, exist_ok=True)

  # Save the private key to a file
  private_key_path = os.path.join(device_dir, "rsa_private.pem")
  with open(private_key_path, "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

  # Save the public key to a file
  public_key_path = os.path.join(device_dir, "rsa_public.pem")
  with open(public_key_path, "wb") as f:
    f.write(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

def update_publisher_keys(publisher):
  """Updates the RSA keys for a publisher.

  Args:
      publisher: A dictionary representing a publisher.
  """
  private_key, public_key = generate_rsa_keypair()

  # # Serialize the private key to PEM format (PKCS#8)
  # publisher["rsaPrivateKey"] = private_key.private_bytes(
  #     encoding=serialization.Encoding.PEM,
  #     format=serialization.PrivateFormat.PKCS8,
  #     encryption_algorithm=serialization.NoEncryption()
  # ).decode("utf-8")

  # # Serialize the public key to PEM format (SubjectPublicKeyInfo)
  # publisher["rsaPublicKey"] = public_key.public_bytes(
  #     encoding=serialization.Encoding.PEM,
  #     format=serialization.PublicFormat.SubjectPublicKeyInfo
  # ).decode("utf-8")
  
  # Serialize the keys to PEM format
  private_key_pem = private_key.private_bytes(
      encoding=serialization.Encoding.PEM,
      format=serialization.PrivateFormat.PKCS8,
      encryption_algorithm=serialization.NoEncryption()
  ).decode("utf-8")
  public_key_pem = public_key.public_bytes(
      encoding=serialization.Encoding.PEM,
      format=serialization.PublicFormat.SubjectPublicKeyInfo
  ).decode("utf-8")

  # Update the publisher with new keys and renamed fields
  publisher["privateKey"] = private_key_pem  # Renamed from rsaPrivateKey
  publisher["publicKey"] = public_key_pem  # Renamed from rsaPublicKey

  # Remove the old key fields
  del publisher["rsaPrivateKey"]
  del publisher["rsaPublicKey"]

  # Save the keys to files
  save_keypair(private_key, public_key, publisher["name"])


def main(argv):
  del argv  # Unused.

  try:
    with open(FLAGS.i, "r") as f:
      data = json.load(f)

    for publisher in data["publishers"]:
      update_publisher_keys(publisher)

    with open(FLAGS.o, "w") as f:
      json.dump(data, f, indent=4)

    print(f"Publishers updated with new RSA keys. "
          f"Changes written to '{FLAGS.o}'")

  except FileNotFoundError:
    print(f"Error: Input file '{FLAGS.i}' not found.")
  except KeyError:
    print(f"Error: 'publishers' array not found in '{FLAGS.i}'.")


if __name__ == "__main__":
  app.run(main)


# from cryptography.hazmat.primitives.asymmetric import rsa
# from cryptography.hazmat.primitives import serialization

# def generate_rsa_key(key_size=2048, filename="rsa_private.pem"):
#     """Generates an RSA private key and saves it to a PEM file.

#     Args:
#         key_size: The size of the RSA key in bits (default: 2048).
#         filename: The name of the file to save the key to (default: "rsa_private.pem").
#     """
#     private_key = rsa.generate_private_key(
#         public_exponent=65537,  # Commonly used public exponent
#         key_size=key_size
#     )

#     pem = private_key.private_bytes(
#         encoding=serialization.Encoding.PEM,
#         format=serialization.PrivateFormat.PKCS8,  # Recommended format
#         encryption_algorithm=serialization.NoEncryption()  # No password
#     )

#     with open(filename, "wb") as f:
#         f.write(pem)

#     print(f"RSA private key saved to {filename}")


# if __name__ == "__main__":
#     generate_rsa_key()  # Or generate_rsa_key(4096, "my_key.pem") for a 4096-bit key