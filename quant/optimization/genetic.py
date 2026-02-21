"""
Genetic algorithm for portfolio optimization
"""

from typing import Callable, Dict, List, Tuple

import numpy as np


class GeneticOptimizer:
    """
    Genetic algorithm for portfolio optimization
    Useful for non-convex, complex objective functions
    """
    
    def __init__(
        self,
        population_size: int = 100,
        generations: int = 200,
        crossover_rate: float = 0.8,
        mutation_rate: float = 0.1,
        elitism: int = 5,
    ):
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism = elitism
    
    def optimize(
        self,
        n_assets: int,
        fitness_func: Callable[[np.ndarray], float],
        constraints: Dict = None,
    ) -> Tuple[np.ndarray, float]:
        """
        Run genetic algorithm optimization
        
        Args:
            n_assets: Number of assets
            fitness_func: Function to maximize
            constraints: Optimization constraints
        
        Returns:
            Best solution and fitness value
        """
        # Initialize population
        population = self._initialize_population(n_assets)
        
        best_fitness_history = []
        
        for generation in range(self.generations):
            # Evaluate fitness
            fitness = np.array([fitness_func(ind) for ind in population])
            
            # Track best
            best_idx = np.argmax(fitness)
            best_fitness = fitness[best_idx]
            best_individual = population[best_idx].copy()
            
            best_fitness_history.append(best_fitness)
            
            if generation % 20 == 0:
                print(f"Gen {generation}: Best fitness = {best_fitness:.4f}")
            
            # Selection
            selected = self._tournament_selection(population, fitness)
            
            # Crossover
            offspring = self._crossover(selected)
            
            # Mutation
            offspring = self._mutate(offspring)
            
            # Elitism: keep best individuals
            elite_indices = np.argsort(fitness)[-self.elitism:]
            elite = population[elite_indices]
            
            # New population
            population = np.vstack([elite, offspring[:self.population_size - self.elitism]])
        
        # Return best solution
        final_fitness = np.array([fitness_func(ind) for ind in population])
        best_idx = np.argmax(final_fitness)
        
        # Normalize to sum to 1
        best_weights = population[best_idx]
        best_weights = best_weights / best_weights.sum()
        
        return best_weights, final_fitness[best_idx]
    
    def _initialize_population(self, n_assets: int) -> np.ndarray:
        """Create random initial population"""
        population = np.random.random((self.population_size, n_assets))
        # Normalize each individual
        population = population / population.sum(axis=1, keepdims=True)
        return population
    
    def _tournament_selection(
        self,
        population: np.ndarray,
        fitness: np.ndarray,
        tournament_size: int = 3,
    ) -> np.ndarray:
        """Tournament selection"""
        selected = []
        
        for _ in range(len(population)):
            # Random tournament
            tournament_idx = np.random.choice(len(population), tournament_size, replace=False)
            tournament_fitness = fitness[tournament_idx]
            winner_idx = tournament_idx[np.argmax(tournament_fitness)]
            selected.append(population[winner_idx])
        
        return np.array(selected)
    
    def _crossover(self, parents: np.ndarray) -> np.ndarray:
        """Uniform crossover"""
        offspring = []
        
        for i in range(0, len(parents), 2):
            parent1 = parents[i]
            parent2 = parents[(i + 1) % len(parents)]
            
            if np.random.random() < self.crossover_rate:
                # Uniform crossover
                mask = np.random.random(len(parent1)) < 0.5
                child1 = np.where(mask, parent1, parent2)
                child2 = np.where(mask, parent2, parent1)
                
                # Normalize
                child1 = child1 / child1.sum()
                child2 = child2 / child2.sum()
                
                offspring.extend([child1, child2])
            else:
                offspring.extend([parent1, parent2])
        
        return np.array(offspring)
    
    def _mutate(self, population: np.ndarray) -> np.ndarray:
        """Mutation"""
        mutated = population.copy()
        
        for i in range(len(mutated)):
            if np.random.random() < self.mutation_rate:
                # Random mutation
                idx = np.random.randint(len(mutated[i]))
                mutated[i, idx] += np.random.normal(0, 0.1)
                
                # Ensure non-negative and normalize
                mutated[i] = np.maximum(mutated[i], 0)
                mutated[i] = mutated[i] / mutated[i].sum()
        
        return mutated
