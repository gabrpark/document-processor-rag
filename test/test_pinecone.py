import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

response = index.query(
		namespace="docs",
    vector=[0.47,0.94,0.92,0.07,0.81,0.82,0.33,0.56,0.29,0.41,0.7,0.59,0.06,0.08,0.54,0,0.56,0.09,0.86,0.38,0.69,0.24,0.72,0.17,0.54,0.78,0.3,0.49,0.89,0.89,0.64,0.55,0.17,0.5,0.98,0.59,0.86,0.42,0.52,0.33,0.6,0.13,0.45,0.99,0.95,0.81,0.51,0.72,0.03,0.56,0.6,0.23,0.5,0,0.42,0.67,0.81,0.83,0.39,0.17,0.73,0.51,0.91,0.02,0.7,0.25,0.83,0.46,0.45,0.58,0.41,0.21,0.08,0.54,0.26,0.61,0.29,0.84,0.08,0.71,0.4,0.47,0.37,0.82,0.56,0.23,0.72,0.82,0.28,0.21,0.03,0.53,0.47,0.46,0.13,0.38,0.31,0.17,0,0.94,0.91,0.68,0.05,0.17,0.9,0.64,0.02,0.41,0.86,0.44,0.59,0.65,0.9,0.01,0.69,0.54,0.77,0.59,0.8,0.35,0.35,0.76,0.13,0.44,0.95,0.24,0.43,0.31,0.55,0.13,0.9,0.92,0.53,0.86,0.2,0.98,0.19,0.05,0.55,0.41,0.39,0.92,0.22,0.18,0.51,0.64,0.85,0.2,0.82,0.98,0.98,0.53,0.38,0.84,0.5,0.53,0.05,0.96,0.32,0.76,0.59,0.53,0.59,0.14,0.63,0.48,0.89,0.57,0.1,0.88,0.52,0.87,0.31,0.28,0.23,0.63,0.73,0.74,0.45,0.41,0.57,0.45,0,0.84,0.11,0.03,0.01,0.79,0.2,0.31,0.91,0.33,0.57,0.79,0.61,0.07,0.14,0.92,0.54,0.52,0.38,0.54,0.54,0.04,0.11,0.13,0.98,0.48,0.96,0.36,0.82,0.6,0.29,0.5,0.12,0.12,0.4,0.99,0.18,0.51,0.87,0.53,0.73,0.72,0.47,0.13,0.01,0.77,0.36,0.21,0.16,0.42,0.99,0.37,0.52,0.23,0.2,0.37,0.51,0.66,0.91,0.19,0.73,0.84,0.34,0.94,0.11,0.96,0.07,0.16,0.16,1,0.56,0.71,0.19,0.69,0.31,0.22,0.87,0.11,0.83,0.4,0.6,0.52,0.31,0.41,0.21,0.13,0.23,0.25,0.34,0.06,0.64,0.1,0.85,0.07,0.82,0.31,0.11,0.66,0.82,0.58,0.13,0.23,0.91,0.56,0.01,0.12,0.37,0.64,0.98,0.87,0.32,0.15,0.73,0.36,0.46,0.33,0.11,0.97,0.18,0.21,0.52,0.33,0.83,0.74,0.46,0.85,0.95,0.69,0.85,0.72,0.03,0.11,0.97,0.89,0.99,0.71,0.48,0.17,0.83,0.53,0.23,0.63,0.2,0.97,0.28,0.46,0.03,0.78,0.28,0.52,0.69,0.6,0.89,0.13,0.83,0.58,0.34,0.53,0.83,0.92,0.84,0.11,0.45,0.93,0.7,0.02,0.91,0.05,0.74,0.52,0.71,0.6,0.36,0.7,0.51,0.23,0.34,0.32,0.42,0.9,0.93,0.92,0.2,0.94,0.74,0.09,0.9,0.54,0.25,0.09,0.88,0.71,0.22,0.82,0.5,0.06,0.38,0.94,0.81,0.47,0.14,0.29,0.74,0.62,0.97,0.79,0.2,0.56,0.49,0.08,0.41,0.15,0,0.1,0.57,0.33,0.93,0.55,0.88,0.34,0.74,0.54,0.67,0.74,0.86,0.37,0.93,0.92,0.15,0.89,0.95,0.59,0.14,0.63,0.31,0.36,0.55,0.57,0.64,0.26,0.38,0.62,1,0.22,0.97,0.13,0.65,0.8,0.49,0.08,0.33,0.82,0.06,0.71,0.44,0.27,0.8,0.06,0.98,0.63,0.04,0.07,0.99,0.57,0.09,0.61,0.36,0.64,0.64,0.92,0.6,0.2,0.05,0.19,0.04,0.64,0.53,0.02,0.17,0.26,0.54,0.4,0.68,0.19,0.25,0.7,0.15,0.35,0.31,0.31,0.01,0.69,0.07,0.2,0.39,0.85,0.78,0.69,0.2,0.59,0.6,0.35,0.19,0.74,0.32,0.38,0.18,0.9,0.47,0.08,0.21,0.85,0.84,0.82,0.84,0.21,0.52,0.13,0.91,0.24,0.44,0.8,0.06,0.66,0.41,0.85,0.22,0.9,0.42,0.94,0.76,0.76,0.69,0.75,0.06,0.99,0.13,0.56,0.35,0.34,0.41,0.81,0.66,0.08,0.27,0.38,0.16,0.83,0.65,0.15,0.13,0,0.18,0.25,0.24,0.11,0.97,0.17,0.87,0.79,0.96,0.25,0.13,0.4,0.69,0.97,0.42,0.27,0.44,0.75,0.63,0.64,0.52,0.76,0.99,0.42,0.28,0.42,0.33,0.99,0.39,0.96,0.21,0.1,0.14,0.97,0.85,0.25,0.46,0.43,0.64,0.89,0.11,0.35,0.17,0.19,0.68,0.08,0.55,0.92,0.68,0.58,0.7,0.25,0.09,0.61,0.71,0.28,0.92,0.15,0.73,0.9,0.58,0.07,0.96,0.18,0.34,0.29,0.44,0.73,0.76,0.94,0.82,0.82,0.03,0.61,0.77,0.49,0.21,0.62,0.51,0.25,0.74,0.1,0.91,0.19,0.18,0.88,0.95,0.55,0.44,0.43,0.12,0.78,0.83,0.62,0.51,0.94,0.31,0.75,0.57,0.27,0.72,0.83,0.79,0.89,0.51,0.88,0.99,0.5,0.54,0.76,0.43,0.98,0.36,0.15,0.94,0.73,0.43,0.04,0.1,0.64,0.55,0.96,0.44,0.26,0.39,0.71,0.69,0.88,0.81,0.38,0.42,0.33,0.52,0.93,0.04,0.75,0.08,0.23,0.02,0.62,0.04,0.48,0.9,0.86,0.2,0.99,0.4,0.57,0.37,0.94,0.79,0.5,0.29,0.44,0.35,0.86,0.23,0.02,0.92,1,0.17,0.09,0.95,0.08,0.05,0.17,0.37,0.09,0.35,0.89,0.5,0.04,1,0.74,0.44,0.02,0.97,0.28,0.82,0.85,0.69,0.62,0.17,0.94,0.82,0.1,0.88,0.39,0.67,0.74,0.31,0.17,0.22,0.76,0.62,0.2,0.67,0.63,0.26,0.5,0.87,0.62,0.84,0.23,0.19,0.69,0.09,0.48,0.95,0.01,0.19,0.91,0.96,0.09,0.44,0.93,0.01,0.15,0.48,0.7,0.98,0.71,0.38,0.59,0.92,0.7,0.89,0.87,0.67,0.95,0.9,0.24,0.13,0.12,0.16,0.57,0.07,0.43,0.47,0.64,0.71,0.02,0.98,0.69,0.53,0.84,0.15,0.34,0.18,1,0.77,0.69,0.75,0.68,0.88,0.49,0.03,0.4,0.51,0.73,0.04,0.93,0.68,0.55,0.08,0.3,0.61,0.32,0.47,0.84,0.96,0.34,0.5,0.56,0.09,0.87,0.93,0.79,0.22,0.92,0.41,0.34,0.43,0.43,0.08,0.66,0.53,0.17,0.79,0.53,0.43,0.45,0.24,0.19,0.36,0.59,0.61,0.09,0.76,0.46,0.42,0.95,0.35,0.78,0.93,0.86,0.82,0.88,0.68,0.34,0.2,0.12,0.41,0.53,0.43,0.25,0.05,0.78,0.2,0.06,0.35,0.23,0.84,0.62,0.28,0.3,0.03,0.11,0.75,0.83,0.33,0.08,0.49,0.67,0.51,0.36,0.04,0.61,0.83,0.91,0.28,0.45,0.4,0.03,0.83,0.24,0.13,0.32,0.93,0.68,0.18,0.51,0.06,0.74,0.16,0.46,0.96,0.45,0.04,0.64,0.18,0.17,0.01,0.55,0.41,0.93,0.64,0.37,0.88,0.49,0.48,0.25,0.35,0.91,0.08,0.02,0.16,0.63,0.57,0.85,0.97,0.25,0.4,0.75,0.05,0.62,0.31,0.47,0.77,0.39,0.25,0.74,0.32,0.89,0.16,0.7,0.32,0.24,0.39,0.88,0.61,0.69,0.69,0.39,0.44,0.28,0.19,0.7,0.86,0.85,0.04,0.58,0.76,0.41,0.88,0.85,0.29,0.25,0.91,0.39,0.92,0.25,0.25,0.29,0.68,0.67,0.51,0.12,0.65,0.71,0.01,0.61,0.97,0.37,0.14,0.84,0.28,0.42,0.33,0.68,0.9,0.47,0.27,0.25,0.85,0.47,0.96,0.47,0.25,0.52,0.31,0.99,0.47,0.35,0.94,0.25,0.4,0.97,0.02,0.7,0.1,0,0.88,0.01,0.15,0.73,0.34,0.28,0.33,0.39,0.18,0.55,0.53,0.95,0.44,0.94,0,0.82,0.14,0.58,0.32,0.76,0.12,0.3,0.59,0.62,0.92,0.46,0.57,0.5,0.74,0.67,0.87,0.21,0.27,0.22,0.42,0.29,0.65,0.87,0.21,0.95,0.35,0.49,0.09,0.16,0.95,0.78,0.53,0.32,0.53,0.52,0.66,0.07,0.51,0.1,0.43,0.51,0.49,0.52,0.26,0.82,0.46,0.34,0.59,0.4,0.36,0.4,0.88,0.18,0.13,0.96,0.81,0.82,0.03,0.39,0.5,0.43,0.55,0.59,0.08,0.63,0.93,0.14,0.47,0.98,0.38,0.15,0.49,0.03,0.11,0.02,0.3,0.54,0.7,0.75,0.03,0.98,0.2,0.2,0.56,0.99,0.72,0.93,0.02,0.88,0.13,0.34,0.26,0.92,0.38,0.8,0.29,0.92,0.84,0.29,0.8,0.79,0.88,0.6,0.15,0.68,0.87,0.31,0.58,0.04,0.67,0.27,0.42,0.32,0.05,0.75,0.06,0.37,0.7,0.17,0.78,0.42,0.74,0.67,0.62,0.4,0.92,0.05,0.82,0.73,0.17,0.04,0.45,0.68,0.65,0.07,0.49,0.96,0.09,0.95,0.39,0.15,0.9,0.93,0.06,0.45,0.08,0.13,0.74,0.78,0.46,0.31,0.81,0.96,0.44,0.06,0.96,0.76,0.78,0.38,0.98,0.16,0.43,0.81,0.67,0.65,0.99,0.89,0.46,0.48,0.26,0.52,0.75,0.49,0.43,0.72,0.3,0.36,0.9,0.19,0.06,0.63,0.38,0.41,0.04,0.88,0.36,0.8,0.67,0.58,0.75,0.01,0.9,0.67,0.12,0.29,0.9,0.77,0.76,0.84,0.87,0.52,0.23,0.52,0.83,0.03,0.81,0.99,0.35,0.06,0.22,0.63,0.58,0.03,0.29,0.94,0.38,0.77,0.31,0.07,0.75,0.02,0.66,0.63,0.1,0.03,0.09,0.81,0.45,0.09,0.39,0,0.84,0.28,0.92,0.96,0.77,0.4,0.61,0.95,0.83,0.98,0,0.12,0,0.66,0.71,0.95,0.22,0.01,0.13,0.1,0.62,0.47,0.78,0.94,0.65,0.53,0.94,0.38,0.56,0.87,0.95,0.18,0.72,0.61,0.08,0.99,0,0.25,0.83,0.48,0.25,0.72,0.64,0.4,0.98,0.24,0.34,0.53,0.03,0.05,0.08,0.38,0.67,0.65,0.43,0.14,0.93,0.18,0.41,0.1,0.92,0.12,0.97,0.94,0.35,0.03,0.01,0.89,0.68,0.04,0.3,0.19,0.52,0.02,0.55,0.84,0.67,0.49,0.44,0.69,0.62,0.93,0.45,0.36,0.11,0.95,0.17,0.09,0.11,0.77,0.62,0.63,0.37,0.82,0.77,0.89,0.09,0.87,0.54,0.56,0.26,0.19,0.45,0.39,0.4,0.4,0.99,0.7,0.34,0.74,0.1,0.54,0.02,0.45,0.31,0.26,0.47,0.25,0.01,0.83,0.44,0.19,0.14,0.48,0.99,0.65,0.97,0.48,0.49,0.28,0.44,0.74,0.56,0,0.83,0.73,0.11,0.46,0.74,0.38,0.87,0.34,0.3,0.05,0.11,0.95,0.23,0.29,0.02,0.3,0.59,0.54,0.29,0.64,0.88,0.08,0.85,0.01,0.72,0.93,0.95,0.43,0.98,0.99,0.59,0.53,0.56,0.82,0.97,0.09,0,0.46,0.04,0.17,0.39,0.64,0.11,0.38,0.66,0.61,0.72,0.37,0.25,0.74,0.18,0.44,0.42,0.85,0.67,0.06,0.37,0.03,0.79,0.86,0.28,0.02,0.58,0.69,0.66,0.83,0.2,0.19,0.99,0.2,0.53,0.86,0.06,0.37,0.87,0.15,0.55,0.77,0.93,0.18,0.63,1,0.1,0.14,0.81,0.67,0.45,0.46,0.28,0.14,0.21,0.14,0.33,0.88,0.8,0.69,0.41,0.09,0.21,0.72,0.44,0.93,0.68,0.23,0.92,0.21,0,0.28,0.3,0.5,0.84,0.78,0.4,0.21,0.27,0.41,0.65,0.74,0.42,0.9,0.58,0.77,0.51,0.42,0.14,0.19,0.39,0.87,0.01,0.61,0.75,0.36,0.16,0.54,0.26,0,0.8,0.82,0.39,0.95,0,0.1,0.18,0.06,0.21,0.9,0.42,0.09,0.66,0.82,0.21,0.43,0.34,0.45,0.61,0.08,0.27,0.38,0.57,0.22],
    top_k=2,
    include_metadata=True
)

print(response)
