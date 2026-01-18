<?php

namespace App\Service;

use Symfony\Component\DependencyInjection\ParameterBag\ParameterBagInterface;

class PythonScriptRunner
{
    private string $pyBin;
    private string $projectRoot;

    public function __construct(ParameterBagInterface $params)
    {
        #$this->pyBin = '/opt/venv/bin/python3';
        $this->pyBin = '/opt/venv/bin/python3';
        $this->projectRoot = $params->get('kernel.project_dir');
    }

    public function run(string $scriptPath, int $userId, string $target): array
    {
        if (!file_exists($this->pyBin)) {
            throw new \RuntimeException("Python env not found at {$this->pyBin}");
        }

        if (!is_dir($this->projectRoot)) {
            throw new \RuntimeException("Project root not found");
        }

        $command = sprintf(
            'cd %s && %s %s %d %s 2>&1',
            escapeshellarg($this->projectRoot),
            escapeshellarg($this->pyBin),
            escapeshellarg($scriptPath),
            $userId,
            escapeshellarg($target)
        );

        $output = shell_exec($command);

        return [
            'command' => $command,
            'output' => $output
        ];
    }
}
