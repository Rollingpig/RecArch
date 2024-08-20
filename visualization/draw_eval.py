import numpy as np
import matplotlib.pyplot as plt
from eval.evaluate import recall, precision

def draw_curve(curve, axis, color, label, linestyle='-'):
    mean_curve = np.mean(curve, axis=0)
    std_curve = np.std(curve, axis=0)
    se_curve = std_curve / np.sqrt(len(curve))
    axis.errorbar([1, 5, 10, 20], mean_curve, yerr=se_curve, fmt='.', color=color)
    axis.plot([1, 5, 10, 20], mean_curve, color=color, label=label, marker='o', linestyle=linestyle)


if __name__ == "__main__":
    label_file_path = "eval/example.csv"
    database_folder_path = "static/indexing"
    result_file_path = "eval/results.csv"
    result_text_only_file_path = "eval/results_text_only.csv"
    result_random_file_path = "eval/results_random.csv"

    # set up a figure with two subplots
    fig, axs = plt.subplots(1, 2, figsize=(7, 3))

    recall_curve = recall(label_file_path, result_file_path)
    recall_text_only_curve = recall(label_file_path, result_text_only_file_path)
    recall_random_curve = recall(label_file_path, result_random_file_path)

    # plot the recall curve
    draw_curve(recall_random_curve, axs[0], 'gray', 'Random method', ':')
    draw_curve(recall_text_only_curve, axs[0], 'g', 'Text only method', '--')
    draw_curve(recall_curve, axs[0], 'b', 'Our method')
    axs[0].set_xticks([1, 5, 10, 20])
    axs[0].set_xlabel("Top-K positions")
    axs[0].set_ylabel("Recall @ K")

    precision_curve = precision(label_file_path, result_file_path)
    precision_text_only_curve = precision(label_file_path, result_text_only_file_path)
    precision_random_curve = precision(label_file_path, result_random_file_path)

    # plot the precision curve
    draw_curve(precision_random_curve, axs[1], 'gray', 'Random method', ':')
    draw_curve(precision_text_only_curve, axs[1], 'g', 'Text only method', '--')
    draw_curve(precision_curve, axs[1], 'b', 'Our method')
    axs[1].set_xticks([1, 5, 10, 20])
    axs[1].set_xlabel("Top-K positions")
    axs[1].set_ylabel("Precision @ K")
    axs[1].legend()

    plt.tight_layout()
    plt.savefig("eval/evaluation.png")