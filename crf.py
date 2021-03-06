import numpy as np
import matplotlib.pyplot as plt

from utils import load_image, whiten

im = load_image('cat1.jpg')
outline = load_image('cat1_outline.png')

# outline consists of 3 values 0, 1, 255. We will igure the value 255.
plt.subplot(1, 2, 1)
plt.imshow(im)
plt.axis('off')
plt.subplot(1, 2, 2)
plt.imshow(outline[..., np.newaxis] * im)
plt.axis('off')
# plt.show()

# Create a grid CRF
N_LABEL = 2
MAX_ITER = 200

feat = whiten(im)
H, W = outline.shape

# indicate whether the node has outline label
label = outline[1:H - 1, 1:W - 1]


def rbf_kernel(dist, sigma=3):
  return np.exp(- np.sum(dist ** 2, 2) / sigma)


# Create pairwise conditional probability with nearest 4 neighbors
curr_feat = feat[1:H - 1, 1:W - 1]
top, bottom, left, right = np.zeros((H, W)), np.zeros(
    (H, W)), np.zeros((H, W)), np.zeros((H, W))

compatibility = np.array([[-2, 0], [0, -2]])
top[1:H - 1,    1:W - 1] = rbf_kernel(curr_feat - feat[0:H - 2, 1:W - 1])
bottom[1:H - 1, 1:W - 1] = rbf_kernel(curr_feat - feat[2:H,     1:W - 1])
left[1:H - 1,   1:W - 1] = rbf_kernel(curr_feat - feat[1:H - 1, 0:W - 2])
right[1:H - 1,  1:W - 1] = rbf_kernel(curr_feat - feat[1:H - 1, 2:W])

# Create unary potential
logit = np.zeros((H, W, N_LABEL))
unary = np.zeros((H, W, N_LABEL))

# Set probabilities
logit[:] = -1

# Set unary potential
unary[outline == 255] = [0, 0]
unary[outline == 0] = [0, -3]
unary[outline == 1] = [-3, 0]

for curr_iter in range(MAX_ITER):
  i = np.random.randint(1, H - 2)
  j = np.random.randint(1, W - 2)

  score = np.exp(logit)
  prob = score / (np.sum(score, 2, keepdims=True) + 1e-6)

  # Pass message
  logit[1:H - 1, 1:W - 1] = (
      left[  1:H - 1, 1:W - 1, np.newaxis] * prob[1:H - 1, 0:W - 2] +
      right[ 1:H - 1, 1:W - 1, np.newaxis] * prob[1:H - 1, 2:W] +
      top[   1:H - 1, 1:W - 1, np.newaxis] * prob[0:H - 2, 1:W - 1] +
      bottom[1:H - 1, 1:W - 1, np.newaxis] * prob[2:H,     1:W - 1]
  ).dot(compatibility) + unary[1:H - 1, 1:W - 1]

  if (curr_iter % 20 == 0):
    z = np.exp(logit[1:H - 1, 1:W - 1])
    p = z / np.sum(z, 2, keepdims=True)
    plt.subplot(1, 2, 1)
    plt.imshow(im)
    plt.axis('off')
    plt.subplot(1, 2, 2)
    plt.imshow(p[..., 0])
    plt.axis('off')
    plt.show()
