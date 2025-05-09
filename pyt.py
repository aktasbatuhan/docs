import matplotlib.pyplot as plt

years = list(range(1, 11))
emission = [14, 12, 10, 8, 7, 6, 5, 4, 3, 2]

plt.figure(figsize=(8,5))
plt.plot(years, emission, marker='o', color='#0D9373', linewidth=3)
plt.fill_between(years, emission, color='#0D9373', alpha=0.15)
plt.title('Emission Schedule', fontsize=16, color='white')
plt.xlabel('Year', fontsize=12, color='white')
plt.ylabel('Annual Emission Rate (%)', fontsize=12, color='white')
plt.xticks(years, color='white')
plt.yticks(range(0, 16, 2), color='white')
plt.grid(alpha=0.3)
plt.gca().set_facecolor('#111827')
plt.gcf().patch.set_facecolor('#111827')
plt.tight_layout()
plt.savefig('emission-schedule.png', dpi=200, transparent=False)
plt.show()